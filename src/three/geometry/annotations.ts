/**
 * Architectural and Documentary 3D Annotation Anchors
 * RUWAQ Historical Documentary Callouts
 */

import { AnnotationItem } from '../../types.ts';

export const BAB_ZUWAYLA_ANNOTATIONS: AnnotationItem[] = [
  {
    id: 'fatimid_bastions',
    titleEn: 'Semicircular Bastion Towers',
    titleAr: 'الأبراج نصف الدائرية الفاطمية',
    date: '1092 CE / 485 AH',
    category: 'fatimid',
    position: [-7.4, 9.0, 3.8],
    descriptionEn:
      'Massive rounded stone bastions commissioned by Armenian Vizier Badr al-Jamali to protect the southern portal of Fatimid al-Qahira. The semicircular geometry was designed to deflect heavy siege artillery and enfilade breaching forces.',
    descriptionAr:
      'أبراج نصف دائرية ضخمة شيدها أمير الجيوش بدر الجمالي لحماية المدخل الجنوبي للقاهرة المعزية، وابتكرت لتشتيت قذائف المجانيق وإتاحة كشف محيط البوابة بالكامل.',
    certainty: 'Historical Record & Archaeological In Situ',
  },
  {
    id: 'cushion_voussoirs',
    titleEn: 'Cushion Voussoirs (الصنجات الوسادية)',
    titleAr: 'الصنجات الوسادية المعقودة',
    date: '1092 CE / 485 AH',
    category: 'masonry',
    position: [0.0, 7.8, 0.4],
    descriptionEn:
      'Signature architectural feature of the northern gates (Bab al-Futuh) and Bab Zuwayla. Convex, pillow-shaped dressed limestone voussoirs that distribute monumental loads across the pointed entrance arch.',
    descriptionAr:
      'السمة المعمارية الفريدة لبوابات القاهرة الفاطمية. صنجات حجرية مصقولة ذات واجهات محدبة كالوسائد تمنح العقد متانة استثنائية وتشتت الأحمال الرأسية.',
    certainty: 'Historical Record & Archaeological In Situ',
  },
  {
    id: 'studded_doors',
    titleEn: 'Iron-Studded Timber Leaves',
    titleAr: 'المصراعان المصفحان بالحديد والمسامير',
    date: '1092 CE / 485 AH',
    category: 'defense',
    position: [-1.4, 3.4, -1.2],
    descriptionEn:
      'Massive hardwood door leaves clad in thick horizontal wrought iron bands secured by hundreds of domed rivets. Originally swung on stone-bushing pivot pins inside the tunnel vault.',
    descriptionAr:
      'مصراعان خشبيان أصليان مصفحان بأشرطة الحديد المشغول ومثبتان بمئات المسامير القبابية الضخمة لصد محاولات الاقتحام وضربات كباش الدك.',
    certainty: 'Historical Record & Archaeological In Situ',
  },
  {
    id: 'machicolation_bridge',
    titleEn: 'Upper Machicolation Bridge',
    titleAr: 'العقد العلوي وسقاطة الدفاع',
    date: '1092 CE / 485 AH',
    category: 'defense',
    position: [0.0, 14.8, -1.2],
    descriptionEn:
      'A spanning arch between the twin bastions creating an upper battle platform with machicolations (open floor slits) to pour boiling liquids and launch missiles directly upon invaders attacking the gate.',
    descriptionAr:
      'جسر علوي مقبى يربط بين البرجين ويشكل سقاطة حربية لصب الزيوت الحارقة وإلقاء المقذوفات مباشرة على المهاجمين أمام البوابة.',
    certainty: 'Historical Record & Archaeological In Situ',
  },
  {
    id: 'mamluk_addition_west',
    titleEn: 'Mamluk Minarets (Twin Additions)',
    titleAr: 'المئذنتان المملوكيتان (إضافات المؤيد شيخ)',
    date: '1415–1421 CE / 818–824 AH',
    category: 'mamluk',
    position: [-7.4, 23.5, 0.0],
    descriptionEn:
      'Three centuries after the gate was built, Sultan al-Mu\'ayyad Shaykh ingeniously utilized the massive Fatimid stone towers as foundations for the twin minarets of his adjoining grand mosque, designed by master architect Muhammad ibn al-Qazzaz.',
    descriptionAr:
      'بعد ثلاثة قرون من بناء البوابة، استغل السلطان المؤيد شيخ متانة الأبراج الفاطمية ليشيد فوقها مئذنتي مسجده الملاصق للبوابة، من إبداع المعمار محمد بن القزاز.',
    certainty: 'Historical Record & Archaeological In Situ',
  },
  {
    id: 'chevron_shaft',
    titleEn: 'Chevron Stone Carving (الزخرفة الزجزاجية)',
    titleAr: 'زخرفة الزجزاج المحفورة بالحجر',
    date: '1415–1421 CE / 818–824 AH',
    category: 'detail',
    position: [7.4, 28.5, 0.0],
    descriptionEn:
      'Interlocking diagonal chevron bands carved deeply into the octagonal limestone shaft, illustrating the height of 15th-century Mamluk stone masonry craftsmanship.',
    descriptionAr:
      'أشرطة هندسية مائلة محفورة بدقة فائقة في الحجر الفص للجذع المثمن، تمثل ذروة الإتقان المعماري في العصر المملوكي الجركسي.',
    certainty: 'Historical Record & Archaeological In Situ',
  },
  {
    id: 'colonnaded_pavilion',
    titleEn: 'Colonnaded Pavilion (Jawsaq / الجوسق)',
    titleAr: 'الجوسق العلوي ذو الأعمدة الحجرية',
    date: '1415–1421 CE / 818–824 AH',
    category: 'mamluk',
    position: [7.4, 34.0, 0.0],
    descriptionEn:
      'Eight slender stone colonnettes supporting horseshoe arches, creating an airy pavilion that elevates the bulbous finial high into the historic Cairo skyline.',
    descriptionAr:
      'رواق مثمن محمول على ثمانية أعمدة حجرية رشيقة تعلوها عقود حدوية، يحمل القمة البصلية في سماء القاهرة التاريخية.',
    certainty: 'Historical Record & Archaeological In Situ',
  },
  {
    id: 'mabkhara_finial',
    titleEn: 'Bulbous Finial (Mabkhara & Hilal)',
    titleAr: 'القمة البصلية (المبخرة) والهلال البرونزي',
    date: '1415–1421 CE / 818–824 AH',
    category: 'detail',
    position: [-7.4, 38.6, 0.0],
    descriptionEn:
      'The iconic bulbous top (often termed Mabkhara or perfume-burner profile) crowned with brass finial spheres and an Islamic crescent moon pointing toward Mecca.',
    descriptionAr:
      'قمة بصلية بديعة التشكيل متوجة بكرات برونزية وهلال نحاسي يرتفع لنحو 40 متراً فوق أرضية شارع المعز.',
    certainty: 'Historical Record & Archaeological In Situ',
  },
];
