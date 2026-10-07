"""VO Studio Finish Chain — Riwaq v1.0
مطابقة بصمة صوتية مرجعية: HPF → body → presence → de-harsh → air-trim →
silence-compress → soft-compress → subtle room → LUFS → true-peak limit
"""
import numpy as np, soundfile as sf, sys, os

SR=44100

def resample(x, sr_in, sr_out=SR):
    if sr_in==sr_out: return x
    n=int(len(x)*sr_out/sr_in); idx=np.linspace(0,len(x)-1,n)
    if x.ndim==1: return np.interp(idx,np.arange(len(x)),x)
    return np.stack([np.interp(idx,np.arange(len(x)),x[:,c]) for c in range(x.shape[1])],1)

def biquad(x, b, a):
    y=np.zeros_like(x); x1=x2=y1=y2=0.0
    for i,v in enumerate(x):
        o=b[0]*v+b[1]*x1+b[2]*x2-a[1]*y1-a[2]*y2
        x2,x1=x1,v; y2,y1=y1,o; y[i]=o
    return y

def peak_eq(x, fc, gain_db, Q):
    A=10**(gain_db/40); w=2*np.pi*fc/SR; al=np.sin(w)/(2*Q); c=np.cos(w)
    b=[1+al*A, -2*c, 1-al*A]; a=[1+al/A, -2*c, 1-al/A]
    return biquad(x, [v/b[0] for v in b], [v/a[0] for v in a])

def high_shelf(x, fc, gain_db, S=0.8):
    A=10**(gain_db/40); w=2*np.pi*fc/SR; c=np.cos(w); s=np.sin(w)
    al=s/2*np.sqrt((A+1/A)*(1/S-1)+2); t=2*np.sqrt(A)*al
    b=[A*((A+1)+(A-1)*c+t), -2*A*((A-1)+(A+1)*c), A*((A+1)+(A-1)*c-t)]
    a=[(A+1)-(A-1)*c+t, 2*((A-1)-(A+1)*c), (A+1)-(A-1)*c-t]
    return biquad(x,[v/a[0] for v in b],[v/a[0] for v in a])

def hpf(x, fc, order=3):
    w=2*np.pi*fc/SR
    for _ in range(order):
        al=np.sin(w)/np.sqrt(2) if False else np.sin(w)/ (2**0.5)
        c=np.cos(w)
        b=[(1+c)/2, -(1+c), (1+c)/2]; a=[1+al, -2*c, 1-al]
        x=biquad(x,[v/a[0] for v in b],[v/a[0] for v in a])
    return x

def fft_band(x, lo, hi, mode='bp'):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR)
    if mode=='lp': g=1/(1+(f/hi)**2)
    elif mode=='hp': g=(f/lo)**2/(1+(f/lo)**2)
    else: g=1/(1+((f-( (lo+hi)/2 ))/((hi-lo)/1.4))**2)
    return np.fft.irfft(X*g,len(x))

# ── loudness (simplified ITU-R BS.1770 / LUFS)
def lufs(x):
    y=high_shelf(x,1500,4.0,1.0); y=hpf(y,38,2)
    bs=int(0.400*SR); st=int(bs*0.25)
    blocks=[y[i:i+bs] for i in range(0,max(1,len(y)-bs),st)]
    def bl(b):
        m=np.mean(b**2)
        return -0.691+10*np.log10(m+1e-12)
    l=[bl(b) for b in blocks]
    l=[v for v in l if v>-70]
    if not l: return -70
    rel=-0.691+10*np.log10(np.mean([10**((v+0.691)/10) for v in l]))-10
    l2=[v for v in l if v>rel]
    if not l2: return -70
    return -0.691+10*np.log10(np.mean([10**((v+0.691)/10) for v in l2]))

def compress(x, thr_db=-20, ratio=2.0, atk=0.012, rel=0.18, makeup_db=3.0, knee=6.0):
    env=np.abs(x); a=np.exp(-1/(atk*SR)); r=np.exp(-1/(rel*SR))
    e=np.zeros_like(env); prev=0.0
    for i,v in enumerate(env):
        prev = a*prev+(1-a)*v if v>prev else r*prev+(1-r)*v
        e[i]=prev
    e_db=20*np.log10(e+1e-9); over=e_db-thr_db
    k=np.clip(over/knee+1,0,2) if knee>0 else (over>0)*2.0
    gain_db=np.where(over>0, -(over*(1-1/ratio))*(k/2), 0)
    return x*10**((gain_db+makeup_db)/20)

def room(x, wet=0.05):
    ir=np.zeros(int(0.09*SR)); rng=np.random.default_rng(4)
    for t,g in [(0.006,.8),(0.013,.6),(0.022,.42),(0.034,.28),(0.05,.18)]: ir[int(t*SR)]+=g
    ir=fft_band(ir,200,5000,'bp'); ir/=np.max(np.abs(ir))
    n=len(x)+len(ir)-1; N=1<<(n-1).bit_length()
    wet_sig=np.fft.irfft(np.fft.rfft(x,N)*np.fft.rfft(ir,N),N)[:len(x)]
    return x*(1-wet)+wet_sig*wet

def compress_silences(x, thresh_db=-42, max_gap_ms=300, target_gap_ms=190):
    env=np.abs(x); win=int(0.01*SR)
    frames=[np.max(env[i:i+win]) for i in range(0,len(x)-win,win)]
    out=[]; i=0; gaps=[]
    thr=10**(thresh_db/20)
    run=0
    for k,v in enumerate(frames):
        if v<thr: run+=1
        else:
            if run*10>max_gap_ms:
                gaps.append((k-run,k,run*10))
            run=0
    if not gaps: return x
    out=[]; last=0
    for s,e,ms in gaps:
        out.append(x[last:s*win])
        keep=int(target_gap_ms/1000*SR)
        mid=(s*win+e*win)//2
        out.append(x[mid-keep//2:mid+keep//2])
        last=e*win
    out.append(x[last:])
    return np.concatenate(out)


def match_reference(x, target_centroid=380, max_boost_db=4.0, step_db=0.6):
    """مطابقة تكيفية: تعدّل رف الحضور حتى يقترب مركز الطيف من المرجع (تحرير آمن، خطوات صغيرة)."""
    boost=0.0
    for _ in range(8):
        c=_centroid(x)
        err=target_centroid-c
        if abs(err) < 25: break
        adj = step_db if err>0 else -step_db*0.8
        boost = float(max(-2.0, min(max_boost_db, boost+adj)))
        # تطبيق تدريجي من الأصل: نشيل الرف السابق ثم نطبقه من جديد
        if getattr(match_reference,'_last',None) is not None:
            x=match_reference._last
        match_reference._last=None
        y=peak_eq(x, 2400, boost, 0.7)          # رف حضور
        y=high_shelf(y, 6500, boost*0.55)        # سطوع خفيف مرتبط
        x=y
    match_reference._last=None
    return x, boost

def true_peak_limit(x, ceiling_db=-1.0):
    c=10**(ceiling_db/20)
    if np.max(np.abs(x))<=c: return x
    x=x/np.max(np.abs(x))*c*1.25
    x=np.tanh(x)
    return x*(c/np.max(np.abs(x)))

def finish(path_in, path_out, target_lufs=-16.0, target_centroid=380, verbose=True):
    d,sr=sf.read(path_in,dtype='float32')
    if d.ndim>1: d=d.mean(axis=1)
    x=resample(d,sr,SR)
    x=x-np.mean(x)
    pre_cent=_centroid(x); pre_f0=_f0(x); pre_lu=lufs(x)
    x=hpf(x,70,3)                                    # 1 تنظيف الترددات المنخفضة
    x=peak_eq(x,250,+2.2,0.9)                        # 2 دِفء الصدر (body)
    x=peak_eq(x,1800,+1.5,0.8)                       # 3 وضوح النطق
    x=peak_eq(x,4200,-2.8,1.1)                       # 4 إزالة الحِدّة (المصدر الرئيسي لإحساس AI)
    x=high_shelf(x,9000,-1.5)                        # 5 تهدئة السطوع الزائد
    x=compress_silences(x)                           # 6 ضغط السكتات → إيقاع طبيعي أسرع
    x=compress(x,-20,2.0,0.012,0.18,3.0)             # 7 ضغط ناعم
    x=room(x,0.05)                                   # 8 غرفة خفيفة (كسر جفاف الـTTS)
    x, boost = match_reference(x, target_centroid)   # 8.5 مطابقة حضور تجاه بصمة المرجع
    if verbose: print(f"    match: حضور {boost:+.1f}dB")
    for _ in range(4):                               # 9 مطابقة الارتفاع (متكررة)
        cur=lufs(x)
        if abs(cur-target_lufs)<0.4: break
        g=min(10**((target_lufs-cur)/20), 3.0)
        x=x*g
        if np.max(np.abs(x))>10**(-1.0/20):
            x=true_peak_limit(x,-1.0)
    x=true_peak_limit(x,-1.0)                        # 10 سقف الذروة الحقيقي
    sf.write(path_out,x,SR,subtype='PCM_16')
    if verbose:
        print(f"  {os.path.basename(path_out)}")
        print(f"    before: LUFS {pre_lu:6.1f} · F0 {pre_f0:5.0f}Hz · centroid {pre_cent:5.0f}Hz")
        print(f"    after : LUFS {lufs(x):6.1f} · F0 {_f0(x):5.0f}Hz · centroid {_centroid(x):5.0f}Hz · peak {20*np.log10(np.max(np.abs(x))):.2f}dB")
    return x

def _f0(x):
    hop=int(0.02*SR); win=int(0.04*SR); out=[]
    for i in range(0,len(x)-win,hop):
        fr=x[i:i+win]
        if np.sqrt(np.mean(fr**2))<0.006: continue
        fr=fr-fr.mean(); ac=np.correlate(fr,fr,'full')[len(fr)-1:]
        lo,hi=int(SR/320),int(SR/60)
        if hi>=len(ac): continue
        pk=lo+int(np.argmax(ac[lo:hi]))
        if ac[0]>0 and ac[pk]/ac[0]>0.3: out.append(SR/pk)
    return float(np.median(out)) if out else 0

def _centroid(x):
    hop=int(0.02*SR); win=int(0.04*SR); cs=[]
    for i in range(0,len(x)-win,hop):
        fr=x[i:i+win]
        if np.sqrt(np.mean(fr**2))<0.006: continue
        S=np.abs(np.fft.rfft(fr*np.hanning(len(fr))))**2; f=np.fft.rfftfreq(len(fr),1/SR)
        cs.append((S*f).sum()/(S.sum()+1e-12))
    return float(np.median(cs)) if cs else 0

if __name__=="__main__":
    import glob
    srcs=sys.argv[1:]
    print("=== VO STUDIO CHAIN — before/after ===")
    for s in srcs:
        out=os.path.join('/home/user/riwaq/08_Audio_Pack/samples_finished','FIN_'+os.path.basename(s))
        finish(s,out)
