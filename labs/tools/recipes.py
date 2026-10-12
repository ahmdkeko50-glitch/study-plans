# -*- coding: utf-8 -*-
# One recipe per lesson file (window.LAB_SIMPLE). Keys: static, adv, advCtl, mainCtl, hide, taps, tapLabel, heroRead, scale, steps
R = {}
R['1-5'] = dict(static=True, heroRead=True,
  advCtl=['طول ضلع', 'فرق جهد البطارية ΔV₀', 'المادّة', 'ثابت العزل', 'قوّة عزل'],
  hide=['مثال \\(2\\)'],
  taps=[dict(label='⬇ قرّب الصفيحتين', key='d', to=1.5), dict(label='⬆ أبعِدهما', key='d', to=8)],
  tapLabel=dict(handle='upper-plate', key='d', a=8, b=1.5, textA='قرّب الصفيحتين', textB='أبعِد الصفيحتين'),
  steps=[
    dict(t='والبطارية مفصولة، <b>قرّب الصفيحتين</b>: اضغط «قرّب الصفيحتين» أو اسحب الصفيحة العلويّة لأسفل حتى <span class="ltr">d &lt; 2 mm</span>.', done='!S.bat && S.d < 2', target='upper-plate', up=1.6),
    dict(t='اقرأ القراءات: <b>ΔV قلّ</b> و<b>C ازدادت</b> والشحنة Q ثابتة.', done='t > 2.5 && !S.bat && S.d < 2'),
    dict(t='<b>أزح الصفيحة جانبًا</b> (أو حرّك منزلق المساحة) حتى تصبح المساحة المتقابلة النصف: C تقلّ.', done='S.ov <= 50', target='upper-plate', up=1.6),
    dict(t='<b>المس الصفيحة العازلة</b> لتدخلها بين الصفيحتين: C تزداد k مرّة.', done='S.slabIn', target='dielectric-slab', up=1.0),
    dict(t='<b>المس المفتاح</b> لتوصل البطارية ثمّ قرّب الصفيحتين: ΔV ثابت و Q تزداد.', done='S.bat && S.d < 3', target='switch', up=1.0)])
R['1-6'] = dict(static=True, heroRead=True,
  advCtl=['سعة C', 'أقصى فرق جهد'], hide=['أعِد كلّ القطع'],
  steps=[
    dict(t='اضغط <b>«مثال (5)»</b>: فرعان على التوازي، في الأوّل C₁ و C₂ على التوالي، وفي الثاني C₃.', done="S.c0 == 20 && S.c1 == 30 && R['المتسعات الموصولة'] >= 3"),
    dict(t='اختر <b>② اختزل التوالي</b>: C₁ و C₂ تصبحان متسعة واحدة <span class="ltr">C′ = 12 µF</span>.', done='S.red >= 1'),
    dict(t='اختر <b>③ السعة المكافئة</b>: <span class="ltr">C′ + C₃ = 30 µF</span>.', done='S.red == 2'),
    dict(t='عُد إلى <b>① الدائرة الأصليّة</b> واقرأ شحنة كلّ متسعة في «لكلّ متسعة».', done='S.red == 0')])
R['1-9'] = dict(heroRead=True, adv=['عناصر الدائرة'],
  steps=[
    dict(t='المس نقطة التماس <b>«شحن»</b> (أو اختر «شحن» هنا) لتغلق المفتاح K.', done="S.pos == 'a'", target='contact-charge', up=0.6),
    dict(t='راقب الجلفانوميتر: التيّار يبدأ <b>أعظميًّا</b> ثمّ يتناقص كلّما شُحنت المتسعة.', done="S.pos == 'a' && t > 3"),
    dict(t='انتظر اكتمال الشحن: <span class="ltr">I = 0</span> و <span class="ltr">ΔV_C = ΔV</span>.', done="S.pos == 'a' && Math.abs(R['التيّار I']) < 0.01 * S.V / (S.Ru * 1e3)"),
    dict(t='<b>المس ذراع المفتاح</b> لتفتحه: الشحنة تبقى على الصفيحتين.', done="S.pos == 'open' && R['الشحنة Q = CΔV_C'] > 0.5 * S.Cu * 1e-6 * S.V", target='switch-handle', up=0.5)])
R['2-3'] = dict(heroRead=True, adv=['الملف والمغناطيس'], advCtl=['حركة آليّة', 'سرعة الحركة الآليّة'],
  patch=[["enabledFn: () => S.mode === 'magnet', onStart: () => { autoCtl(false); glideT = null; }", "onStart: () => { autoCtl(false); glideT = null; if (S.mode !== 'magnet') modeCtl.set('magnet'); }"],
         ["ctx.drag(rig.coilG, { axis: [1, 0, 0], enabledFn: () => S.mode === 'coil', onStart: () => { autoCtl(false); glideT = null; }", "ctx.drag(rig.coilG, { axis: [1, 0, 0], hint: 'اسحب الملف', hintOffset: [0, 2.0, 0], onStart: () => { autoCtl(false); glideT = null; if (S.mode !== 'coil') modeCtl.set('coil'); }"]],
  steps=[
    dict(t='<b>قرّب المغناطيس</b> إلى الملف: اضغط «قرّب» أو اسحبه، وراقب مؤشّر الكلفانوميتر.', done="Math.abs(R['موقع المغناطيس بالنسبة للملف']) < 8", target='magnet-carrier'),
    dict(t='<b>اتركه ساكنًا</b> داخل الملف (اضغط «أوقفه في الوسط»): المؤشّر يعود إلى الصفر.', done="Math.abs(R['موقع المغناطيس بالنسبة للملف']) < 8 && Math.abs(R['السرعة النسبيّة v']) < 0.005 && t > 1.5"),
    dict(t='<b>أبعِد المغناطيس</b>: ينحرف المؤشّر بالاتّجاه المعاكس.', done="Math.abs(R['موقع المغناطيس بالنسبة للملف']) > 15"),
    dict(t='<b>اسحب الملف</b> نفسه نحو المغناطيس الساكن: النتيجة نفسها (الحركة النسبيّة هي المهمّة).', done="S.mode == 'coil' && Math.abs(R['السرعة النسبيّة v']) > 0.05", target='coil-assembly', up=2.2)])
R['2-11'] = dict(scale=3, adv=['المغناطيس والصفيحتان'], mainCtl=['التصوير الحراريّ'], advCtl=['زاوية الإطلاق'],
  steps=[
    dict(t='اضغط <b>«أطلِقهما معًا»</b> (أو اسحب صفيحة جانبًا وأفلتها).', done='!isNaN(H)'),
    dict(t='راقب: <b>الكاملة تتوقّف</b> بعد تأرجحة أو اثنتين بين القطبين، والمقطّعة تستمرّ.', done='t > 8 && !isNaN(H)'),
    dict(t='شغّل <b>التصوير الحراريّ</b> وأطلِقهما مرّة أخرى: أين تولّدت الحرارة؟', done='S.thermal && t > 4')])
R['2-12'] = dict(heroRead=True, adv=['الملف والمجال'], hide=['50 Hz'],
  steps=[
    dict(t='راقب الملف يدور: القوّة الدافعة ε <b>تتغيّر</b> بين الصفر وقيمة عظمى (المنحني في الأسفل).', done='t > 3'),
    dict(t='اقرأ: ε عظمى حين الفيض صفر <span class="ltr">(ωt = 90°)</span>، وتنعدم حين الفيض أعظم <span class="ltr">(ωt = 0)</span>.', done='t > 4'),
    dict(t='اضغط <b>«أوقف الملف»</b>: لا دوران ⇒ لا تغيّر في الفيض ⇒ <span class="ltr">ε = 0</span>.', done='Math.abs(H) < 0.01 && t > 1'),
    dict(t='بدّل التوصيل إلى <b>التيّار المستمرّ</b> (الإعدادات المتقدّمة) وأعِد الدوران: الفولطيّة لا تعكس إشارتها.', done="S.type != 'ac' && Math.abs(H) > 0.5")])
R['2-14'] = dict(heroRead=True, adv=['الملف والمصباحان'], mainCtl=['اجعل R = مقاومة الملف'], hide=['أعد التجربة'],
  steps=[
    dict(t='<b>أغلق المفتاح</b> (المسه أو شغّل المفتاح هنا): أيّ مصباح يضيء أوّلًا؟', done='S.on', target='switch', up=0.8),
    dict(t='راقب تيّار فرع الملف I₂ يرتفع <b>تدريجيًّا</b> (الملف يعارض تزايد التيّار).', done='S.on && t > 4'),
    dict(t='<b>افتح المفتاح</b>: ومضة في المصباحين من ق.د.ك الذاتيّة للملف.', done='!S.on && t > 0.5'),
    dict(t='اضغط «اجعل R = مقاومة الملف» وأغلق المفتاح مرّة أخرى: المصباحان يتساويان في النهاية.', done='S.R == S.Rc && S.on')])
R['2-16'] = dict(heroRead=True, adv=['الدائرة', 'مثال'],
  steps=[
    dict(t='اضغط <b>«أغلق المفتاح»</b>: يسري التيّار في الملف وتُختزن فيه طاقة <span class="ltr">½LI²</span>.', done='S.on', target='switch-pivot', up=0.8),
    dict(t='اضغط <b>«افتح بسرعة (2 ms)»</b>: ق.د.ك ذاتيّة كبيرة — هل أومض النيون؟', done='!S.on && S.tOpen <= 2.5'),
    dict(t='أغلق المفتاح ثمّ <b>«افتح ببطء (300 ms)»</b>: ق.د.ك أصغر فلا يومض.', done='!S.on && S.tOpen >= 200')])
R['3-5'] = dict(heroRead=True,
  steps=[
    dict(t='حرّك منزلق <b>التيّار المستمرّ I</b> (أو اسحبه في المشهد) حتى يتساوى التسخين في السخّانين.', done='Math.abs(S.Idc - S.Im / Math.SQRT2) < 0.1', target='dc-slider'),
    dict(t='اقرأ النسبة <span class="ltr">I/Iₘ ≈ 0.707</span>: هذه هي القيمة المؤثّرة للتيّار المتناوب.', done='t > 2.5 && Math.abs(S.Idc - S.Im / Math.SQRT2) < 0.1'),
    dict(t='غيّر Iₘ (أدِر المقبض) وكرّر: النسبة لا تتغيّر.', done='S.Im != 4 && Math.abs(S.Idc - S.Im / Math.SQRT2) < 0.1', target='source-knob')])
R['3-8'] = dict(heroRead=True, adv=['عناصر الدائرة'],
  steps=[
    dict(t='أدِر مفتاح التردّد (أو حرّك منزلق f) وراقب توهّج المصباح والتيّار.', done='S.f != 1200', target='source-knob'),
    dict(t='ابحث عن التردّد الذي يكون فيه التيّار أعظم، ثمّ اضغط «اضبط على الرنين f₀» وقارن.', done="Math.abs(S.f - R['تردد الرنين f₀ = 1/(2π√(LC))']) < 0.02 * R['تردد الرنين f₀ = 1/(2π√(LC))']"),
    dict(t='عند الرنين: <span class="ltr">XL = XC</span> و <span class="ltr">Z = R</span>. تحقّق من القراءات.', done='t > 3')])
R['3-9'] = dict(static=True, adv=['قيم الدائرة'])
R['3-11'] = dict(heroRead=True, adv=['المقاومة R'],
  steps=[
    dict(t='أدِر قرص التردّد حتى يتوهّج المصباح بأقصى سطوع (أو اضغط «اضبط على الرنين»).', done="Math.abs(R['الممانعة Z'] - S.R) < 0.03 * S.R", target='frequency-knob'),
    dict(t='اقرأ: عند الرنين <span class="ltr">Z = R</span> والتيّار أعظم ما يمكن.', done="t > 2.5 && Math.abs(R['الممانعة Z'] - S.R) < 0.03 * S.R"),
    dict(t='غيّر R من «الإعدادات المتقدّمة» وكرّر: الرنين عند التردّد نفسه لكنّ القمّة أقلّ.', done='S.R != 200')])
R['4-2'] = dict(heroRead=True, advCtl=['الوسط', 'زاوية مستوي', 'مدّة الدورة', 'سعة المجال'],
  steps=[
    dict(t='<b>اسحب المِجَسّ</b> على محور الانتشار وراقب E و B عنده: يتغيّران معًا.', done='S.xp != 2', target='probe'),
    dict(t='اقرأ النسبة <span class="ltr">E/B = c</span> في كلّ موضع.', done='t > 2.5'),
    dict(t='غيّر <b>التردّد</b> (الأُسّ n): يقصر λ ويبقى E/B ثابتًا.', done='S.lf != 8'),
    dict(t='<b>أدِر حلقة الهوائيّ</b>: يدور مستوى E ويبقى B عموديًّا عليه وعلى اتّجاه الانتشار.', done='S.psi != 0', target='em-wave')])
R['4-3'] = dict(heroRead=True, adv=['حلقة الكشف'], mainCtl=['وضع هرتز'], advCtl=['مدّة الدورة', 'إظهار نمط'],
  steps=[
    dict(t='راقب <b>الشرارة</b> في فجوة حلقة الكشف وهي بلا أيّ سلك يصلها بالمُرسِل.', done="t > 3"),
    dict(t='اضغط <b>«قطر الرنين πD = λ»</b>: الشرارة أقوى حين يساوي محيط الحلقة طول الموجة.', done='S.D != 0.95'),
    dict(t='<b>اسحب الحلقة لتدويرها</b> (فجوة عموديّة): تضعف الشرارة.', done='(S.roll != 0 || S.yaw != 0) && t > 1', target='detector-rotor'),
    dict(t='<b>أبعِد الحلقة</b> عن المُرسِل (اسحب قاعدتها): تضعف الإشارة مع البُعد.', done='S.r > 8', target='detector')])
R['4-10'] = dict(heroRead=True, scale=2, adv=['الهوائيّ'],
  steps=[
    dict(t='راقب الهوائيّ يدور: حين يمرّ على الطائرة يظهر صداها على الشاشة.', done='t > 4'),
    dict(t='اضغط <b>«مثال الكتاب: t = 400 µs»</b> واقرأ المدى <span class="ltr">d = ct/2 = 60 km</span>.', done="Math.abs(R['المدى d = c·t/2'] - 60000) < 1500 || Math.abs(R['المدى d = c·t/2'] - 60) < 1.5"),
    dict(t='<b>اسحب الطائرة</b> أبعد: يزداد زمن الصدى ويزداد المدى.', done='S.dSel > 100 && S.dSel != 181', target='target-0', up=1.5)])
R['5-2'] = dict(heroRead=True, advCtl=['سرعة الموجة', 'سعة اهتزاز', 'موقع المؤشّر x', 'موقع المؤشّر z', 'إظهار المسارين'], hide=['Δℓ = 1.5λ', 'Δℓ = 2.5λ'],
  steps=[
    dict(t='<b>اسحب المؤشّر</b> فوق الماء وراقب فرق المسار Δℓ ونوع التداخل.', done='S.px != 5.6 || Math.abs(S.pz - 14.4) > 0.01', target='probe'),
    dict(t='اضغط <b>«ضع المؤشّر على أقرب خطّ عُقديّ»</b>: <span class="ltr">Δℓ = (m + ½)λ</span> ⇒ تداخل إتلافيّ والسطح ساكن.', done="Math.abs((R['Δℓ/λ · فرق الطور Φ'] % 1) - 0.5) < 0.08"),
    dict(t='شغّل <b>وضع التحليل</b>: الخطوط الخضراء بنّاءة والحمراء إتلافيّة.', done='S.analysis'),
    dict(t='قلّل المسافة d بين الرأسين: تتباعد الخطوط العُقديّة.', done='S.d < 5')])
R['5-3'] = dict(static=True, heroRead=True, adv=['الشقّان', 'القياس'], mainCtl=['موقع المؤشّر على الشاشة', 'رتبة الهدب'], hide=['المنضدة كلّها', 'مثال \\(3\\)', 'تحقّق: Δy'],
  steps=[
    dict(t='<b>اسحب المؤشّر</b> على الشاشة إلى مركز الهدب المضيء الثاني واضبط الرتبة <span class="ltr">m = 2</span>.', done='S.m == 2 && Math.abs(S.y - 2 * S.lam * S.L / S.d * 1e-3) < 0.3', target='screen-pointer', up=0.6),
    dict(t='اقرأ <b>λ المحسوبة</b> = y·d/(m·L) وقارنها بالقيمة الحقيقيّة.', done='t > 2.5'),
    dict(t='شغّل <b>«مصدر مجهول»</b> وقِس λ بنفسك بالطريقة نفسها.', done='S.mystery && S.m >= 2 && Math.abs(S.y - S.m * S.lam * S.L / S.d * 1e-3) < 0.3'),
    dict(t='بدّل إلى <b>ضوء أبيض</b>: الهدب المركزيّ أبيض وحوافّ الأهداب ملوّنة.', done='S.white')])
R['5-5'] = dict(static=True, heroRead=True, adv=['العرض'], hide=['ℓ = 100λ', 'ℓ = 3λ'],
  steps=[
    dict(t='<b>أدِر البكرة</b> (أو حرّك المنزلق) لتضييق الشقّ: راقب اتّساع الهدب المركزيّ.', done='S.ratio < 15', target='drum'),
    dict(t='اضغط <b>«ℓ = λ»</b>: الهدب المركزيّ يملأ الشاشة كلّها (الحيود أعظم ما يمكن).', done='S.ratio <= 1.05'),
    dict(t='وسّع الشقّ إلى <span class="ltr">ℓ = 100λ</span> بالمنزلق: يكاد الضوء يسير مستقيمًا.', done='S.ratio >= 80')])
R['5-7'] = dict(static=True, heroRead=True, adv=['الضوء'], hide=['θ = 45°'],
  steps=[
    dict(t='<b>أدِر المحلِّل</b> حتى <span class="ltr">θ = 90°</span>: ينطفئ الضوء النافذ.', done='Math.abs((((S.beta - S.alpha) % 180) + 180) % 180 - 90) < 4', target='analyser-rotor'),
    dict(t='اقرأ: <span class="ltr">I/I₀ = cos²θ = 0</span>.', done='t > 2'),
    dict(t='أدِر إلى <span class="ltr">θ = 60°</span>: ينفذ ربع الشدّة فقط.', done='Math.abs((((S.beta - S.alpha) % 180) + 180) % 180 - 60) < 4'),
    dict(t='أزِل <b>المستقطِب</b> من المسار: لا يتغيّر النافذ بتدوير المحلِّل (الضوء غير مستقطَب).', done='!S.usePol')])
R['6-3'] = dict(heroRead=True, adv=['القياس والرسم', 'المعدن'], advCtl=['بُعد المصباح', 'نافذة الخلية'], hide=['ضوء أحمر على الصوديوم'],
  patch=[["hintOffset: [0.9, -1.35, 0.7], enabledFn: () => pred.choice != null,", "hintOffset: [0.9, -1.35, 0.7],"]],
  steps=[
    dict(t='التردّد الآن أقلّ من عتبة الصوديوم: <b>لا تيّار</b>. ارفع <b>الشدّة</b> — لا شيء يتغيّر.', done='S.P != 40'),
    dict(t='ارفع <b>التردّد f</b> فوق f₀ (أدِر قرص التردّد): يظهر التيّار فجأة.', done='S.f > 0.6', target='frequency-drum'),
    dict(t='اضغط <b>«مثال (2): λ = 300 nm على الصوديوم»</b> واقرأ Kmax وجهد القطع V₀.', done='Math.abs(S.f - 1.0) < 0.03'),
    dict(t='غيّر <b>المعدن</b> من الإعدادات المتقدّمة: دالّة الشغل φ تحدّد تردّد العتبة f₀.', done='S.metal != 0')])
R['6-5'] = dict(heroRead=True, adv=['البلّورة'], hide=['1.5×10⁶', '2×10⁷', 'امسح الشاشة'],
  steps=[
    dict(t='اضغط <b>«أطلق 3000 إلكترون»</b> وراقب الحلقات تتكوّن على الشاشة.', done="R['إلكترونات على الشاشة'] > 500"),
    dict(t='ارفع <b>سرعة الإلكترون</b> (أدِر المقبض): λ تقصر والحلقات تضيق.', done='S.v > 8e6', target='speed-knob'),
    dict(t='أزِل البلّورة من طريق الحزمة (الإعدادات المتقدّمة): تختفي الحلقات.', done="!S['in']")])
R['6-9'] = dict(heroRead=True, adv=['الجهاز'], mainCtl=['أدِر 90°'],
  steps=[
    dict(t='اختر أنموذج <b>«الأثير»</b> ثمّ اضغط «أدِر 90°»: تنزاح الأهداب كما توقّع العلماء.', done="S.model != 'real' && Math.abs(S.th) >= 45"),
    dict(t='اختر <b>«الواقع»</b> وأدِر 90° مرّة أخرى: <b>لا إزاحة</b>.', done="S.model == 'real' && Math.abs(S.th % 360) >= 45 && t > 1"),
    dict(t='الاستنتاج: سرعة الضوء واحدة في الذراعين — لا أثير.', done='t > 3')])
R['6-11'] = dict(heroRead=True, adv=['العرض'], hide=['0.8c', 'صفّر الساعتين'],
  steps=[
    dict(t='اضغط <b>«ساكنة»</b>: الساعتان تدقّان معًا.', done='S.b == 0'),
    dict(t='اضغط <b>«0.6c»</b>: مسار الضوء أطول عند الراصد الساكن، فساعة المركبة أبطأ.', done='Math.abs(S.b - 0.6) < 0.01 && t > 3'),
    dict(t='اقرأ <span class="ltr">γ = 1.25</span>: لكلّ 1 s عند الراصد تسجّل المركبة 0.8 s.', done='t > 3 && Math.abs(S.b - 0.6) < 0.01'),
    dict(t='<b>اسحب المقبض نحو c</b> (0.99c): تكاد ساعة المركبة تتوقّف.', done='S.b > 0.95', target='speed-knob')])
R['7-6'] = dict(heroRead=True, adv=['درجة الحرارة'], advCtl=['نسبة التطعيم'],
  steps=[
    dict(t='<b>اسحب ذرّة أنتيمون Sb</b> إلى البلّورة (أو حرّك منزلقها): يظهر إلكترون حرّ زائد.', done='S.nSb >= 1', target='dopant-Sb'),
    dict(t='اقرأ: نوع البلّورة <b>N</b>، الأغلبيّة إلكترونات، وصافي الشحنة صفر.', done='t > 2.5 && S.nSb >= 1'),
    dict(t='اضغط «بلّورة نقيّة» ثمّ اسحب ذرّة <b>بورون B</b>: تظهر فجوة — نوع P.', done='S.nB >= 1 && S.nSb == 0', target='dopant-B')])
R['7-8'] = dict(heroRead=True, adv=['البلّورة'], advCtl=['مدى فولطية', 'المقاومة المتوالية'],
  steps=[
    dict(t='أغلق المفتاح والانحياز <b>أماميّ</b>: يمرّ التيّار ويضيق حاجز الجهد.', done='S.on && S.pol == 1 && t > 1', target='switch'),
    dict(t='ارفع فولطيّة البطاريّة: التيّار يرتفع بسرعة بعد نحو <span class="ltr">0.7 V</span> (سليكون).', done='S.on && S.pol == 1 && S.eps > 1.5'),
    dict(t='اضغط <b>«اقلب البطارية»</b> (انحياز عكسيّ): يتّسع الحاجز ويكاد التيّار ينعدم.', done='S.pol == -1 && S.on', target='battery')])
R['7-10'] = dict(static=True, heroRead=True, hide=['مثال \\(2\\)'], advCtl=['ربح التيّار α', 'مقاومة الدخول', 'مقاومة الخروج'],
  steps=[
    dict(t='اضغط <b>«مثال (1)»</b> واقرأ Vin و Vout وربح الفولطيّة Av.', done='t > 3'),
    dict(t='غيّر <b>تيّار الباعث I_E</b> (اسحب المنزلق): يتغيّر IC = αIE وتبقى النسبة.', done='S.IE != 3', target='rheostat-slider'),
    dict(t='أدِر مقبض المولّد لتغيير سعة الإشارة: الإشارة الخارجة أكبر لأنّ <span class="ltr">R_out &gt; R_in</span>.', done='S.m != 20', target='generator-knob')])
R['8-2'] = dict(heroRead=True, adv=['الحزمة الكاملة', 'الرقاقة'], hide=['امسح المسارات', 'b = 100 fm'],
  steps=[
    dict(t='اضغط <b>«🚀 أطلق الدقيقة»</b> ببُعد تصويب <span class="ltr">b = 40 fm</span> وراقب انحرافها.', done='t > 3'),
    dict(t='اضغط «صوّب إلى المركز b = 0» ثمّ أطلق: ترتدّ الدقيقة إلى الخلف.', done='S.b == 0 && t > 2'),
    dict(t='شغّل <b>الحزمة الكاملة</b> من الإعدادات المتقدّمة: واحدة من آلاف الدقائق ترتدّ.', done="S.beam || R['عدد الدقائق المطلقة'] > 1000")])
R['8-3'] = dict(heroRead=True, adv=['إثارة'], hide=['حدّ السلسلة', 'امسح الشريط'],
  steps=[
    dict(t='اضغط <b>«⬇ نفّذ الانتقال»</b> من <span class="ltr">n = 3</span> إلى <span class="ltr">n = 2</span>: فوتون أحمر (خطّ Hα).', done="S.ni == 3 && S.nf == 2 && t > 2"),
    dict(t='اجعل <span class="ltr">n_i = 4</span> ونفّذ: فوتون أزرق (طاقة أكبر وطول موجيّ أقصر).', done='S.ni == 4 && S.nf == 2'),
    dict(t='اجعل <span class="ltr">n_f = 1</span> (سلسلة ليمان): فوق بنفسجيّ غير مرئيّ.', done='S.nf == 1')])
R['8-6'] = dict(heroRead=True, adv=['التصوير الشعاعيّ'], advCtl=['شدّة تسخين', 'مادّة الهدف'], hide=['ضع المؤشّر يسار λmin'],
  steps=[
    dict(t='شغّل <b>تسخين الفتيل</b> (المس المفتاح): تنطلق الإلكترونات وتظهر الأشعّة.', done='S.heat && t > 1'),
    dict(t='اقرأ <b>λmin</b> عند <span class="ltr">V = 50 kV</span>، ثمّ ارفع V (أدِر القرص): تقصر λmin.', done='S.V > 60', target='voltage-knob'),
    dict(t='<b>اسحب مؤشّر الكاشف</b> إلى يسار λmin: لا أشعّة أقصر منها مهما كانت شدّة الفتيل.', done='S.lamD < 1240 / S.V', target='detector-cursor')])
R['8-7'] = dict(heroRead=True, advCtl=['أو: فرق جهد', 'تكبير Δλ', 'حركة الفوتون'], hide=['مثال \\(2\\)', 'θ = 0°', 'θ = 180°'],
  steps=[
    dict(t='<b>أدِر ذراع الكاشف</b> إلى <span class="ltr">θ = 90°</span>: <span class="ltr">Δλ = 2.43 pm</span> (طول موجة كومبتون).', done='Math.abs(S.th - 90) < 3', target='detector-arm'),
    dict(t='أدِر إلى <span class="ltr">θ = 180°</span>: أكبر زيادة <span class="ltr">Δλ = 4.86 pm</span>.', done='S.th > 175'),
    dict(t='عُد إلى <span class="ltr">θ = 0°</span>: لا تغيّر في الطول الموجيّ.', done='S.th < 5')])
R['8-9'] = dict(heroRead=True, advCtl=['قدرة المصدر', 'انفراج المصباح'],
  steps=[
    dict(t='اضغط <b>«⚡ أطلق نبضة»</b> بالليزر وراقب زمن الذهاب والإياب <span class="ltr">≈ 2.56 s</span>.', done="R['زمن الذهاب والإياب t'] > 1"),
    dict(t='اقرأ قطر البقعة على القمر: بضعة كيلومترات فقط.', done='t > 2.5'),
    dict(t='بدّل إلى <b>المصباح</b> وأطلق: البقعة أكبر آلاف المرّات والشدّة لا تُذكر.', done="S.src != 'laser' && t > 1")])
R['9-2'] = dict(static=True, heroRead=True, adv=['نوى الكتاب'],
  steps=[
    dict(t='أضف <b>نيوترونًا</b> واحدًا (اسحبه أو اضغط «+ نيوترون»): يتغيّر A لا العنصر (نظير).', done='S.Z == 13 && S.N == 15', target='neutron-tray-token'),
    dict(t='أضف <b>بروتونًا</b>: يتغيّر <b>العنصر</b> نفسه، فالعدد الذرّيّ Z هو الذي يحدّده.', done='S.Z == 14', target='proton-tray-token'),
    dict(t='ابنِ نواة <b>الذهب</b> من «نوى الكتاب» (الإعدادات المتقدّمة) واقرأ A والكتلة والطاقة.', done='S.Z == 79')])
R['9-3'] = dict(static=True, heroRead=True, hide=['^\\d{1,3}(H|He|Li|C|N|O|Fe|U)$', 'U ← نواتان', 'H \\+ '],
  steps=[
    dict(t='<b>اسحب المؤشّر</b> على المنحنى (أو المس عمودًا) إلى اليورانيوم <span class="ltr">A = 238</span>.', done='S.A > 200', target='selector'),
    dict(t='اضغط <b>«🔻 اشطر النواة نصفين»</b>: الناتجان أعلى على المنحنى ⇒ تتحرّر طاقة.', done="R['طاقة آخر عمليّة'] > 0"),
    dict(t='اختر <b>²H</b> واضغط «🔺 ادمج نواتين»: تتحرّر طاقة أيضًا (الخفيفة تندمج).', done="S.A == 2 && R['طاقة آخر عمليّة'] > 0")])
R['9-4'] = dict(heroRead=True, adv=['النواة الأمّ', 'طاقة انحلال', 'فوتون كاما'],
  steps=[
    dict(t='اضغط <b>«انحلال الآن»</b> (ألفا): A ينقص 4 و Z ينقص 2.', done='S.A == 236 && S.Z == 92'),
    dict(t='اختر <b>بيتا السالبة</b> ثمّ انحلال: Z يزيد 1 و A لا يتغيّر.', done='S.Z == 93'),
    dict(t='اختر <b>كاما</b> (نواة متهيّجة): لا يتغيّر A ولا Z، ويخرج فوتون.', done="/g|γ|كاما/.test(String(S.mode)) && t > 1")])
R['9-6'] = dict(heroRead=True, adv=['الطاقة المتحرّرة'],
  steps=[
    dict(t='اضغط <b>«نيوترون حراريّ 0.025 eV»</b> ثمّ <b>«أطلق النيوترون»</b>: تنشطر النواة.', done='t > 4'),
    dict(t='تحقّق من <b>حفظ A و Z</b> في القراءات.', done='t > 3'),
    dict(t='ارفع طاقة النيوترون (سريع) وأطلق: احتمال الانشطار أقلّ.', done='S.lgE > 3')])
