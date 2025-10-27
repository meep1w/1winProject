// ===== Telegram WebApp init =====
const tg = window.Telegram?.WebApp;
try { tg?.ready(); tg?.expand(); } catch (_) {}

const qs  = (s, p = document) => p.querySelector(s);
const qsa = (s, p = document) => [...p.querySelectorAll(s)];
const params = new URLSearchParams(location.search);

// ===== Langs =====
const SUP_LANGS = [
    { code: "ru", label: "Русский", short: "RU" },
    { code: "en", label: "English", short: "EN" },
    { code: "hi", label: "हिन्दी", short: "HI" },
    { code: "pt", label: "Português", short: "PT" },
    { code: "es", label: "Español", short: "ES" },
    { code: "ui", label: "Українська", short: "UKR" },
    { code: "tr", label: "Türkçe", short: "TR" },
    { code: "in", label: "Indonesia", short: "ID" },
    { code: "fr", label: "Français", short: "FR" },
    { code: "ozbek", label: "Oʻzbek", short: "UZ" },
    { code: "de", label: "Deutsch", short: "DE" },
];

const lang = (params.get("lang") || "ru").toLowerCase();
const ref  = params.get("ref") || "";

// ===== i18n =====
const i18n = {
    ru:{ title:"1win Return to Player", subtitle:"Прокачай RTP уже сегодня <br> с 10.10.25 по 10.01.26.\nПовысь шансы на победу вместе с 1win", cta:"Подробнее" },
    en:{ title:"1win Return to Player", subtitle:"Boost your RTP today from 10.10.25 to 10.01.26.\nIncrease your chances of winning with 1win", cta:"Learn more" },
    hi:{ title:"1win Return to Player", subtitle:"आज ही अपना RTP बढ़ाएँ 10.10.25 से 10.01.26 तक।\n1win के साथ जीतने की संभावना बढ़ाएँ", cta:"और जानें" },
    pt:{ title:"1win Return to Player", subtitle:"Aumente seu RTP hoje de 10.10.25 a 10.01.26.\nAumente suas chances de vitória com a 1win", cta:"Saiba mais" },
    es:{ title:"1win Return to Player", subtitle:"Potencia tu RTP hoy del 10.10.25 al 10.01.26.\nAumenta tus posibilidades de ganar con 1win", cta:"Más detalles" },
    ui:{ title:"1win Return to Player", subtitle:"Прокачай RTP вже сьогодні з 10.10.25 по 10.01.26.\nЗбільшуй шанси на перемогу разом з 1win", cta:"Докладніше" },
    tr:{ title:"1win Return to Player", subtitle:"RTP'ni bugün artır — 10.10.25–10.01.26 arasında.\n1win ile kazanma şansını yükselt", cta:"Daha fazla" },
    in:{ title:"1win Return to Player", subtitle:"Tingkatkan RTP kamu hari ini dari 10.10.25 hingga 10.01.26.\nTingkatkan peluang menangmu dengan 1win", cta:"Selengkapnya" },
    fr:{ title:"1win Return to Player", subtitle:"Boostez votre RTP dès aujourd’hui du 10.10.25 au 10.01.26.\nAugmentez vos chances de gagner avec 1win", cta:"En savoir plus" },
    ozbek:{ title:"1win Return to Player", subtitle:"RTP’ni bugunoq oshiring, 10.10.25 dan 10.01.26 gacha.\n1win bilan gʻalaba imkoniyatini ko‘paytiring", cta:"Batafsil" },
    de:{ title:"1win Return to Player", subtitle:"Steigere dein RTP noch heute vom 10.10.25 bis 10.01.26.\nErhöhe deine Gewinnchancen mit 1win", cta:"Mehr erfahren" },
};
const t = (k)=> (i18n[lang] || i18n.ru)[k];

qs("#title").textContent  = t("title");
qs("#subtitle").innerHTML = t("subtitle").replace(/\n/g,"<br/>");
qs("#ctaBtn").textContent = t("cta");

// ===== Lang dropdown =====
const langWrap = qs("#langDropdown");
const langBtn  = qs("#langBtn");
const langMenu = qs("#langMenu");
const langFlag = qs("#langFlag");
const langCode = qs("#langCode");

function setCurrentLang(code){
    const found = SUP_LANGS.find(x => x.code === code) || SUP_LANGS[0];
    langFlag.src = `./static/img/flags/${found.code}.svg`;
    langFlag.alt = found.short;
    langCode.textContent = found.short;
}
function renderLangMenu(){
    langMenu.innerHTML = "";
    SUP_LANGS.forEach(({code,label,short})=>{
        const li = document.createElement("li");
        const b = document.createElement("button");
        b.type="button"; b.setAttribute("role","option");
        b.innerHTML = `<img class="lang__flag" src="./static/img/flags/${code}.svg" alt="${short}"> ${label} (${short})`;
        b.addEventListener("click", ()=>{
            const q = new URLSearchParams(location.search);
            q.set("lang", code); if (ref) q.set("ref", ref);
            location.search = q.toString();
        });
        li.appendChild(b); langMenu.appendChild(li);
    });
}
renderLangMenu(); setCurrentLang(lang);

langBtn?.addEventListener("click", ()=>{
    const open = !langMenu.classList.contains("open");
    langMenu.classList.toggle("open", open);
    langWrap.classList.toggle("lang--open", open);
    langBtn.setAttribute("aria-expanded", String(open));
});
document.addEventListener("click", (e)=>{
    if (!langMenu.contains(e.target) && !langBtn.contains(e.target)) {
        langMenu.classList.remove("open");
        langWrap?.classList.remove("lang--open");
        langBtn?.setAttribute("aria-expanded","false");
    }
});

// ===== Smooth scroll =====
(() => {
    const btn = qs('#ctaBtn');
    const target = qs('#rtp-cards .rtp-stack__title') || qs('#rtp-cards');
    if (!btn || !target) return;
    const getHeaderH = () =>
        parseInt(getComputedStyle(document.documentElement).getPropertyValue('--header-h').trim() || '0', 10) || 0;

    btn.addEventListener('click', (e) => {
        e.preventDefault();
        const prefersReduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
        const y = target.getBoundingClientRect().top + window.scrollY - getHeaderH();
        window.scrollTo({ top: y, behavior: prefersReduce ? 'auto' : 'smooth' });
    });
})();

// ===== FAQ accordion =====
(() => {
    const list = qs('#faqList'); if (!list) return;
    list.querySelectorAll('.accordion__btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const expanded = btn.getAttribute('aria-expanded') === 'true';
            list.querySelectorAll('.accordion__btn[aria-expanded="true"]').forEach(b=>{
                if (b !== btn) b.setAttribute('aria-expanded','false');
            });
            btn.setAttribute('aria-expanded', String(!expanded));
            try { window.Telegram?.WebApp?.HapticFeedback?.selectionChanged(); } catch(_) {}
        });
    });
})();

// ===== Modal helpers =====
const openModals = new Set();
function lockScroll(){ document.documentElement.style.overflow = openModals.size ? 'hidden' : ''; }
function openModal(el){
    if (!el) return; el.classList.add('open'); openModals.add(el); lockScroll();
    const sheet = el.querySelector('.modal__sheet'); sheet?.focus?.({preventScroll:true});
}
function closeModal(el){
    if (!el) return; el.classList.remove('open','loading'); openModals.delete(el); lockScroll();
    el.querySelectorAll('.select__menu.open').forEach(m=>m.classList.remove('open'));
    el.querySelectorAll('[aria-expanded="true"]').forEach(b=>b.setAttribute('aria-expanded','false'));
}
document.addEventListener('click', (e)=>{
    const modal = e.target.closest('.modal');
    if (e.target.matches('[data-close]')) closeModal(modal);
});
document.addEventListener('keydown', (e)=>{
    if (e.key !== 'Escape') return; const top = Array.from(openModals).pop(); if (top) closeModal(top);
});

// ===== Terms =====
const TERMS_HTML = `<div class="terms">
    <h4 style="margin:0 0 10px;">Правила и условия акции «1win Traffic Race»</h4>

    <p><b>Период акции:</b> 10 октября 2025 — 10 января 2026.</p>

    <h5>1. Участники</h5>
    <ul>
      <li>К участию допускаются пользователи 18+ с подтверждённым аккаунтом 1win.</li>
      <li>Один участник — один аккаунт. Дубли/мульти-аккаунты дисквалифицируются.</li>
      <li>Организатор оставляет за собой право проверять данные победителей.</li>
    </ul>

    <h5>2. Как участвовать</h5>
    <ul>
      <li>Зарегистрируйте <b>новый</b> аккаунт по реферальной ссылке на странице.</li>
      <li>Активируйте участие с помощью <b>промокода</b> в разделе «Увеличить RTP».</li>
      <li>Играйте в краш-играх с минимальной ставкой от 38 ₽ и множителем от ×2.2.</li>
    </ul>

    <h5>3. Начисление очков</h5>
    <ul>
      <li>Очки начисляются по внутр. формуле на основе суммы множителей выигрышных раундов.</li>
      <li>Лидерборд обновляется ориентировочно <b>каждый час</b> (возможны задержки).</li>
      <li>Подозрительная активность (накрутка, сговор) аннулирует очки.</li>
    </ul>

    <h5>4. Призы</h5>
    <ul>
      <li>Призовой фонд: <b>1 260 000 ₽</b>, распределение см. в разделе «Все призы».</li>
      <li>Итоги подводятся после окончания акции. Победители уведомляются в боте/по e-mail.</li>
      <li>Невостребованные призы могут быть перераспределены согласно правилам площадки.</li>
    </ul>

    <h5>5. Ограничения и ответственность</h5>
    <ul>
      <li>Организатор может изменять сроки и механики при форс-мажоре, сообщая на странице акции.</li>
      <li>Запрещены любые попытки технического или финансового злоупотребления.</li>
      <li>Участник несёт ответственность за корректность данных и сохранность доступа к аккаунту.</li>
    </ul>

    <h5>6. Персональные данные</h5>
    <ul>
      <li>Данные обрабатываются для целей участия и вручения призов согласно политике конфиденциальности 1win.</li>
    </ul>

    <p style="margin-top:10px;color:#6b7280;">Участвуя в акции, вы подтверждаете согласие с указанными правилами.</p>
  </div>`;
(() => {
    const modal = qs('#termsModal'); if (!modal) return;
    const content = qs('#modalContent');
    [qs('#infoBtn'), qs('#footerTermsBtn')].filter(Boolean).forEach(b=>{
        b.addEventListener('click', ()=>{ content.innerHTML = TERMS_HTML; openModal(modal); });
    });
})();

// ===== RTP FORM → open button =====
qsa('.rtp-card__btn')[0]?.addEventListener('click', ()=> openModal(qs('#rtpModal')));

// ===== Custom GEO select =====
const GEO = [
    { code:'ru', name:'Russia' },
    { code:'ww', name:'Worldwide (EN)' },
    { code:'in', name:'India' },
    { code:'br', name:'Brazil' },
    { code:'es', name:'Spain' },
    { code:'ui', name:'Ukraine' },
    { code:'tr', name:'Türkiye' },
    { code:'id', name:'Indonesia' },
    { code:'fr', name:'France' },
    { code:'ozbek', name:'Uzbekistan' },
    { code:'de', name:'Germany' },
];
(() => {
    const btn  = qs('#geoBtn'); const menu = qs('#geoMenu'); const flag = qs('#geoFlag');
    const label= qs('#geoLabel'); const hidden = qs('#f_geo'); if (!btn || !menu) return;

    menu.innerHTML = '';
    const head = document.createElement('li');
    head.innerHTML = `<div style="font-weight:700;padding:10px 12px;color:#6b7280;">ГЕО</div>`; menu.appendChild(head);
    GEO.forEach(({code, name})=>{
        const li = document.createElement('li'); const b = document.createElement('button');
        b.type='button'; b.className='select__opt';
        b.innerHTML = `<img src="./static/img/flags/${code}.svg" alt=""><span>${name}</span>`;
        b.addEventListener('click', ()=>{
            hidden.value = code; label.textContent = name; flag.src = `./static/img/flags/${code}.svg`; flag.hidden = false;
            btn.setAttribute('aria-expanded','false'); menu.classList.remove('open','dropup');
        });
        li.appendChild(b); menu.appendChild(li);
    });

    function placeMenu(){
        const r = btn.getBoundingClientRect();
        const spaceBelow = window.innerHeight - r.bottom;
        const estHeight = Math.min(260, menu.scrollHeight || 260);
        menu.classList.toggle('dropup', spaceBelow < estHeight + 16);
    }
    btn.addEventListener('click', ()=>{
        const open = !menu.classList.contains('open'); if (open) placeMenu();
        menu.classList.toggle('open', open); btn.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', (e)=>{
        if (!menu.contains(e.target) && !btn.contains(e.target)) { menu.classList.remove('open','dropup'); btn.setAttribute('aria-expanded','false'); }
    });
})();

// ===== Toast (верхняя ошибка) =====
function showToast(msg='Введены не верные данные'){
    const t = qs('#pageToast'); if (!t) return;
    t.textContent = msg; t.classList.add('show');
    setTimeout(()=> t.classList.remove('show'), 2600);
}

// ===== Storage helpers =====
const LS_KEY = 'rtpFormData_v1';
function loadSaved(){ try{ return JSON.parse(localStorage.getItem(LS_KEY)||'null'); }catch{ return null; } }
function saveData(data){ localStorage.setItem(LS_KEY, JSON.stringify(data)); }
function sameForm(a,b){
    return a && b && a.name===b.name && a.account===b.account && a.tg===b.tg && a.geo===b.geo;
}

// ===== Percent generation =====
function weightedRandomPercent(){
    const p = Math.random();
    if (p < 0.15) { return Math.floor(Math.random()*35); }
    return 35 + Math.floor(Math.random()*41);
}
function driftAround(v){
    const delta = Math.round((Math.random()*6)-3);
    let n = v + delta; if (n < 0) n = 0; if (n > 75) n = 75; return n;
}

// ===== Gauge (по твоей иконке) =====
function gaugeSVG(percent){
    const activeIdx = (percent < 35) ? 0 : (percent < 75 ? 1 : 2);
    const cls = (i) => {
        if (i !== activeIdx) return 'seg-base';
        return activeIdx === 0 ? 'active-red' : (activeIdx === 1 ? 'active-blue' : 'active-green');
    };
    return `
<svg viewBox="0 0 263 132" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <defs>
    <linearGradient id="gRed" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#ff8a8a"/><stop offset="100%" stop-color="#de4343"/></linearGradient>
    <linearGradient id="gBlue" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#5aa8ff"/><stop offset="100%" stop-color="#2f6fff"/></linearGradient>
    <linearGradient id="gGreen" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#34d399"/><stop offset="100%" stop-color="#10b981"/></linearGradient>
  </defs>
  <path class="${cls(0)}" d="M54.4221 25.0372C58.0024 22.4485 62.962 23.5735 65.3294 27.3038L77.9749 47.2296C80.3422 50.9601 79.2122 55.8766 75.7005 58.5577C65.5011 66.3447 57.0111 76.1904 50.801 87.4864L50.2259 88.548C44.3581 99.5598 40.793 111.625 39.718 124.01L39.6731 124.42C39.1317 128.496 35.8723 131.781 31.7835 131.989L31.3714 132H7.77179L7.35968 131.989C3.13174 131.775 -0.245138 128.277 0.0139779 124.005C1.19481 104.544 6.67463 85.5511 16.0989 68.4083C25.5232 51.2656 38.6238 36.4617 54.4221 25.0372Z"/>
  <path class="${cls(1)}" d="M133.248 0.0078125C152.137 0.219213 170.738 4.48238 187.799 12.4805C191.799 14.3558 193.221 19.2386 191.107 23.1182L179.814 43.8408L179.607 44.1973C177.397 47.8046 172.725 49.0612 168.804 47.3457C157.443 42.3758 145.175 39.7336 132.73 39.6045L131.524 39.6006C118.666 39.6349 105.986 42.3521 94.2867 47.5449L93.9058 47.7031C90.0753 49.1988 85.624 47.9335 83.4664 44.4541L83.2584 44.0986L71.855 23.4365C69.7201 19.5683 71.1165 14.6779 75.107 12.7812C92.6745 4.43141 111.902 0.0520127 131.419 0L133.248 0.0078125Z"/>
  <path class="${cls(2)}" d="M207.802 25.0372C204.222 22.4485 199.263 23.5735 196.895 27.3038L184.25 47.2296C181.882 50.9601 183.012 55.8766 186.524 58.5577C196.723 66.3447 205.213 76.1904 211.424 87.4864L211.999 88.548C217.866 99.5598 221.432 111.625 222.507 124.01L222.551 124.42C223.093 128.496 226.352 131.781 230.441 131.989L230.853 132H254.453L254.865 131.989C259.093 131.775 262.47 128.277 262.211 124.005C261.03 104.544 255.55 85.5511 246.126 68.4083C236.701 51.2656 223.601 36.4617 207.802 25.0372Z"/>
</svg>`;
}

// ===== Render result modal =====
function renderResultModal(data){
    const modal = qs('#resultModal'); if (!modal) return;
    const content = modal.querySelector('.modal__content'); if (!content) return;

    const geoObj  = GEO.find(g => g.code === data.geo);
    const geoName = geoObj?.name || data.geo;
    const geoFlag = geoObj ? `./static/img/flags/${geoObj.code}.svg` : '';

    content.innerHTML = `
    <div class="result">
      <div class="result__gauge">
        <div class="gauge">
          ${gaugeSVG(data.percent)}
          <div class="gauge__label">
            <div class="gauge__cap">Процент RTP</div>
            <div class="gauge__val">${data.percent}%</div>
          </div>
        </div>
      </div>

      <dl class="result__list">
        <dt class="result__term">Имя</dt><dd class="result__val">${data.name}</dd>
        <dt class="result__term">ID Account</dt><dd class="result__val">${data.account}</dd>
        <dt class="result__term">Telegram</dt><dd class="result__val">${data.tg}</dd>
        <dt class="result__term">ГЕО</dt>
        <dd class="result__val"><span class="result__geo">${geoFlag ? `<img src="${geoFlag}" alt="">` : ''}<span>${geoName}</span></span></dd>
      </dl>

      <div class="result__hr"></div>
      <p class="result__note">При повторных проверках значение RTP может незначительно меняться — это нормально. Мы учитываем актуальные параметры аккаунта и игры.</p>
    </div>
  `;

    const okBtn = modal.querySelector('.modal__footer .modal__ok');
    if (okBtn) {
        okBtn.textContent = 'Увеличить RTP';
        okBtn.onclick = () => { closeModal(modal); renderBoostModal(); openModal(qs('#boostModal')); };
    }
}

// ===== RTP form submit =====
(() => {
    const modal = qs('#rtpModal'); if (!modal) return;
    const submit = qs('#rtpSubmit', modal);
    const loader = qs('#rtpLoader', modal);
    const inputs = { name: qs('#f_name'), account: qs('#f_account'), tg: qs('#f_tg'), geo: qs('#f_geo') };

    function validate(){
        let ok = true;
        Object.values(inputs).forEach(el=>{
            const val = (el.value || '').trim();
            if (!val) { ok = false; const f = el.id==='f_geo' ? qs('#geoBtn') : el; f.classList.add('shake'); setTimeout(()=>f.classList.remove('shake'), 360); }
        });
        return ok;
    }
    function startLoading(){ modal.classList.add('loading'); loader?.setAttribute('aria-busy','true'); }
    function stopLoading(){  modal.classList.remove('loading'); loader?.removeAttribute('aria-busy'); }

    submit.addEventListener('click', (e)=>{
        e.preventDefault();
        if (!validate()) return;

        const current = {
            name: inputs.name.value.trim(),
            account: inputs.account.value.trim(),
            tg: inputs.tg.value.trim(),
            geo: inputs.geo.value.trim()
        };

        const saved = loadSaved();
        let percent;

        if (saved) {
            if (!sameForm(saved, current)) {
                showToast('Введены не верные данные');
                return;
            }
            percent = driftAround(saved.percent);
        } else {
            percent = weightedRandomPercent();
        }

        startLoading();
        setTimeout(()=>{
            stopLoading();
            const toSave = { ...current, percent };
            saveData(toSave);
            closeModal(modal);
            renderResultModal(toSave);
            openModal(qs('#resultModal'));
        }, 3200);
    });
})();

// ====== BOOST MODAL: рефка, промокоды, копирование ======
const DEFAULT_REF_LINK = 'https://1win.example/register?ref=YOUR_DEFAULT_REF';
const PROMO_CODES = ['WIN75', 'RTPPLUS', '1WINLUCK', 'TOPRTP', 'BOOST75'];

const LS_PROMO_IDX = 'rtpPromoIdx_v1';
const LS_REF_URL   = 'rtpRefUrl_admin_v1';   // сюда может писать бот
const LS_PROMO_USED = 'rtpPromoUsed_v1';     // флаг «пользователь скопировал промо»

function getRefLink(){
    const urlParam = params.get('refUrl') || params.get('refurl') || params.get('ref');
    if (urlParam) return urlParam;
    try {
        const fromAdmin = localStorage.getItem(LS_REF_URL);
        if (fromAdmin) return fromAdmin;
    } catch {}
    return DEFAULT_REF_LINK;
}
function nextPromo(){
    let idx = 0;
    try {
        idx = parseInt(localStorage.getItem(LS_PROMO_IDX) || '0', 10);
        if (Number.isNaN(idx)) idx = 0;
    } catch {}
    const code = PROMO_CODES[idx % PROMO_CODES.length];
    try { localStorage.setItem(LS_PROMO_IDX, String((idx + 1) % PROMO_CODES.length)); } catch {}
    return code;
}
async function copyText(text){
    try {
        await navigator.clipboard.writeText(text);
        try { window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred('success'); } catch {}
        try { localStorage.setItem(LS_PROMO_USED, '1'); } catch {}
        return true;
    } catch { return false; }
}

function renderBoostModal(){
    const modal = qs('#boostModal'); if (!modal) return;
    const content = modal.querySelector('.modal__content');
    const footer  = modal.querySelector('.modal__footer');

    const promo = nextPromo();
    const refLink = getRefLink();

    content.innerHTML = `
    <div class="boost">
      <div class="boost__text" style="background:#f7f9fc;border-radius:12px;padding:14px 12px;margin-bottom:14px;">
        <p style="margin:0 0 8px;"><b>Как повысить RTP?</b> Зарегистрируй новый аккаунт 1win по нашей ссылке. На свежих аккаунтах выше вероятность получить повышенный RTP и участвовать в розыгрышах.</p>
        <p style="margin:0;">Для участия используй <b>промокод</b> ниже — он активирует участие в конкурсах и подарках.</p>
      </div>

      <div class="boost__cta" style="margin:0 0 16px;">
        <a class="btn btn--primary modal__ok boost__btn" href="${refLink}" target="_blank" rel="noopener noreferrer" style="display:block;text-align:center;">
          Зарегистрировать новый
        </a>
      </div>

      <div class="boost__section-title" style="text-align:center;font-weight:800;margin:0 0 10px;">Ваш промокод</div>

      <button id="promoCopy" class="promo" type="button" aria-label="Скопировать промокод"
        style="width:100%;border:1px solid #e5e7eb;border-radius:12px;padding:12px;cursor:pointer;background:#fff;">
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;">
          <span class="promo__code" id="promoCode" style="font:800 20px/1 Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;letter-spacing:1px;">${promo}</span>
          <span class="promo__hint" id="promoHint" style="font:600 12px/1.2 Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#9aa3b2;">Нажмите, чтобы скопировать</span>
        </div>
      </button>

      <div class="boost__note" style="margin:12px 0 0;color:#6b7280;font:600 12px/1.4 Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;text-align:center;">
        Промокод нужен, чтобы засчиталось участие в розыгрышах и активировались спец-условия. При следующем визите код может быть другим — так и задумано.
      </div>
    </div>
  `;
    footer.innerHTML = `<button class="btn btn--primary modal__ok" type="button" data-close>Закрыть</button>`;

    const copyBtn  = qs('#promoCopy', content);
    const codeEl   = qs('#promoCode', content);
    const hintEl   = qs('#promoHint', content);

    copyBtn?.addEventListener('click', async () => {
        const ok = await copyText(codeEl?.textContent?.trim() || '');
        if (ok && hintEl) {
            const prev = hintEl.textContent;
            hintEl.textContent = 'Скопировано!';
            hintEl.style.color = '#16a34a';
            setTimeout(() => { hintEl.textContent = prev; hintEl.style.color = '#9aa3b2'; }, 1600);
        }
    });
}

/* ===================== PARTICIPATE (карточка №2) ===================== */
/* Требования показа:
   - пользователь наш реферальный и ввёл любой из промокодов.
   - для локальной проверки можно добавить ?debug=1 в URL.
*/

const LS_PARTICIPATE_JOINED = 'rtp_participate_joined';
const LS_USED_PROMO         = 'rtp_used_promo_v1';   // ставит бот после ввода промо
const LS_IS_REF             = 'rtp_is_ref_v1';       // ставит бот при переходе по реф-ссылке

// ====== URL игры (может меняться из бота/админки) ======
const LS_PLAY_URL = 'rtpPlayUrl_admin_v1'; // сюда бот кладёт актуальный URL игры
function getPlayUrl(){
    // приоритет: ?play=... → localStorage из админки → дефолт
    return (
        params.get('play') ||
        (()=>{
            try { return localStorage.getItem(LS_PLAY_URL) || ''; } catch { return ''; }
        })() ||
        'https://1wfmzx.life/casino/fast-games/crash-games' // дефолт
    );
}
// ======================================================

function isJoined() {
    try { return localStorage.getItem(LS_PARTICIPATE_JOINED) === '1'; } catch { return false; }
}
function setJoined(v) {
    try { localStorage.setItem(LS_PARTICIPATE_JOINED, v ? '1' : '0'); } catch {}
}
function hasParticipateAccess() {
    if (params.get('debug') === '1') return true; // локальная проверка
    try {
        return localStorage.getItem(LS_USED_PROMO) === '1' && localStorage.getItem(LS_IS_REF) === '1';
    } catch { return false; }
}

/* ——— модалка «Как участвовать» ——— */
function ensureParticipateModal() {
    let modal = document.getElementById('participateModal');
    if (modal) return modal;

    modal = document.createElement('div');
    modal.id = 'participateModal';
    modal.className = 'modal modal--65';
    modal.setAttribute('aria-hidden', 'true');
    modal.innerHTML = `
    <div class="modal__backdrop" data-close></div>
    <section class="modal__sheet" role="dialog" aria-modal="true" aria-labelledby="participateTitle" tabindex="-1">
      <header class="modal__header">
        <h3 id="participateTitle">Как участвовать</h3>
        <button class="modal__x" type="button" aria-label="Закрыть" data-close>✕</button>
      </header>
      <div class="modal__content"></div>
      <div class="modal__footer"></div>
    </section>
  `;
    document.body.appendChild(modal);
    return modal;
}

function renderParticipateModal() {
    const modal   = ensureParticipateModal();
    const content = modal.querySelector('.modal__content');
    const footer  = modal.querySelector('.modal__footer');
    const joined  = isJoined();
    const PLAY_URL = getPlayUrl();

    const step1Inner = joined
        ? `<div class="pill pill--muted" aria-live="polite">Вы участвуете</div>`
        : `<button id="pJoinBtn" class="btn btn--primary btn--sm">Участвовать</button>`;

    content.innerHTML = `
    <div class="participate">
      <div class="steps">
        <div class="step">
          <div class="step__badge">Шаг 1</div>
          <div class="step__title">Жмите «Участвовать»</div>
          <div class="step__spacer"></div>
          <div class="step__action">${step1Inner}</div>
        </div>
        <div class="step">
          <div class="step__badge">Шаг 2</div>
          <div class="step__title">Ставьте в кражах от 38 ₽, множитель — от ×2.2</div>
          <div class="step__spacer"></div>
          <div class="step__action">
            <a id="pPlayBtn"
               class="btn btn--secondary btn--sm"
               href="${PLAY_URL}"
               target="_blank" rel="noopener noreferrer">Играть</a>
          </div>
        </div>
      </div>

      <div class="participate__links">
        <button id="pPrizesBtn" class="btn btn--ghost btn--grad">Все призы</button>
      </div>

      <p class="participate__note">
        Играйте активно в период акции — чем больше оборот и выше множители, тем больше шансов.
        Рейтинг обновляется регулярно, следите за прогрессом.
      </p>

      <h4 class="lb__title">Лидерборд</h4>
      <div class="lb__subtitle">Рейтинг по сумме множителей <span class="lb__hint">обновляем ~каждый час</span></div>

      <div class="lb__table">
        <div class="lb__row lb__row--head"><div>Место</div><div>ID игрока</div><div>Баллы</div></div>
        <div class="lb__row"><div>1</div><div>***37666</div><div>14189.31</div></div>
        <div class="lb__row"><div>2</div><div>***959347</div><div>11489.59</div></div>
        <div class="lb__row"><div>3</div><div>***381811</div><div>10728.26</div></div>
        <div class="lb__row"><div>4</div><div>***931405</div><div>7698.35</div></div>
        <div class="lb__row"><div>5</div><div>***88779</div><div>7557.17</div></div>
        <div class="lb__row"><div>6</div><div>***36064</div><div>5353.59</div></div>
        <div class="lb__row"><div>7</div><div>***917448</div><div>4789.68</div></div>
        <div class="lb__row"><div>8</div><div>***949822</div><div>4696.68</div></div>
        <div class="lb__row"><div>9</div><div>***363695</div><div>4653.18</div></div>
        <div class="lb__row"><div>10</div><div>***83210</div><div>4494.09</div></div>
      </div>

      <div class="participate__close">
        <button class="btn btn--primary" data-close>Закрыть</button>
      </div>
    </div>
  `;
    footer.innerHTML = '';

    const joinBtn = content.querySelector('#pJoinBtn');
    if (joinBtn) {
        joinBtn.addEventListener('click', () => {
            setJoined(true);
            const host = joinBtn.parentElement;
            host.innerHTML = `<div class="pill pill--muted" aria-live="polite">Вы участвуете</div>`;
            try { window.Telegram?.WebApp?.HapticFeedback?.selectionChanged?.(); } catch {}
        });
    }

    // Открытие игры корректно внутри Telegram WebApp
    const playBtn = content.querySelector('#pPlayBtn');
    playBtn?.addEventListener('click', (e) => {
        if (tg?.openLink) {
            e.preventDefault();
            tg.openLink(PLAY_URL, { try_instant_view: false });
        }
    });

    content.querySelector('#pPrizesBtn')?.addEventListener('click', () => {
        // здесь можешь открыть модалку «Все призы» или сделать скролл
        try { window.Telegram?.WebApp?.HapticFeedback?.selectionChanged?.(); } catch {}
    });
}

/* ——— привязка к карточке №2 ——— */
(function bindParticipateCard() {
    const card2Btn = qsa('.rtp-card')[1]?.querySelector('.rtp-card__btn'); // «Участвовать» во 2-й карточке
    if (!card2Btn) return;

    card2Btn.addEventListener('click', () => {
        if (!hasParticipateAccess()) {
            // showToast('Доступ к разделу получают участники по реф-ссылке и с промокодом');
            return;
        }
        renderParticipateModal();
        openModal(ensureParticipateModal());
    });
})();

/* ——— отладка для локалки ———
   window.__dbgPlay('<url>') — положить свою ссылку в localStorage (как сделает бот)
*/
window.__dbgPlay = (url) => {
    try { localStorage.setItem(LS_PLAY_URL, url); } catch {}
};
/* =================== /PARTICIPATE =================== */

/* ===================== PRIZES MODAL (v2, красивее) ===================== */
function ensurePrizesModal() {
    let modal = document.getElementById('prizesModal');
    if (modal) return modal;

    modal = document.createElement('div');
    modal.id = 'prizesModal';
    modal.className = 'modal modal--65';
    modal.setAttribute('aria-hidden', 'true');
    modal.innerHTML = `
    <div class="modal__backdrop" data-close></div>
    <section class="modal__sheet" role="dialog" aria-modal="true" aria-labelledby="prizesTitle" tabindex="-1">
      <header class="modal__header">
        <h3 id="prizesTitle">Призы</h3>
        <button class="modal__x" type="button" aria-label="Закрыть" data-close>✕</button>
      </header>
      <div class="modal__content"></div>
      <div class="modal__footer"></div>
    </section>
  `;
    document.body.appendChild(modal);
    return modal;
}

function renderPrizesModal() {
    const modal   = ensurePrizesModal();
    const content = modal.querySelector('.modal__content');
    const footer  = modal.querySelector('.modal__footer');

    const PRIZES = [
        { place: '1 место',        amount: '56 700 ₽' },
        { place: '2 место',        amount: '50 400 ₽' },
        { place: '3 место',        amount: '44 100 ₽' },
        { place: '4 место',        amount: '37 800 ₽' },
        { place: '5 место',        amount: '31 500 ₽' },
        { place: '6–40 места',     amount: '15 120 ₽' },
        { place: '41–75 места',    amount: '10 080 ₽' },
        { place: '76–100 места',   amount: '6 300 ₽'  },
    ];

    content.innerHTML = `
    <div class="prizes">
      <div class="prizes__fund">Призовой фонд — <span>1&nbsp;260&nbsp;000 ₽</span></div>

      <div class="prizes__list">
        ${PRIZES.map(p => `
          <div class="prize">
            <div class="prize__left">
              <div class="prize__badge">${p.place}</div>
            </div>
            <div class="prize__right">
              <div class="prize__amount">${p.amount}</div>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;

    footer.innerHTML = `
    <div class="prizes__footer">
      <button id="prBackBtn" class="btn btn--ghost prizes__btn">Назад</button>
      <button class="btn btn--primary prizes__btn" type="button" data-close>Закрыть</button>
    </div>
  `;

    footer.querySelector('#prBackBtn')?.addEventListener('click', () => {
        closeModal(modal);
        renderParticipateModal?.();
        openModal(ensureParticipateModal());
    });
}

/* делегирование на «Все призы» из модалки участия */
document.addEventListener('click', (e) => {
    const btn = e.target.closest('#pPrizesBtn');
    if (!btn) return;
    const part = document.getElementById('participateModal');
    if (part) closeModal(part);
    renderPrizesModal();
    openModal(ensurePrizesModal());
});

/* ===== локальные стили (аккуратные плашки и синяя «Закрыть») ===== */
(() => {
    const css = `
  /* заголовок фонда */
  .prizes__fund{
    font:800 16px/1.25 Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
    color:#0f172a; margin-bottom:14px;
  }
  .prizes__fund span{ font-weight:900; letter-spacing:0.2px }

  /* список */
  .prizes__list{ display:flex; flex-direction:column; gap:10px }
  .prize{
    display:grid; grid-template-columns:1fr auto; align-items:center;
    padding:12px 14px; border-radius:14px;
    background:linear-gradient(180deg,#f7f9fd 0%, #eef2f8 100%);
    border:1px solid #e6ecf5; box-shadow:0 1px 0 rgba(17,24,39,.03) inset;
    transition:transform .08s ease, box-shadow .15s ease;
  }
  .prize:hover{ transform:translateY(-1px); box-shadow:0 6px 18px rgba(31,41,55,.08) }
  .prize__badge{
    display:inline-block; padding:7px 12px; border-radius:999px;
    background:#e9f0ff; color:#1e3a8a;
    font:700 12px/1 Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
    letter-spacing:.1px; border:1px solid #d9e6ff;
  }
  .prize__amount{
    padding:7px 12px; border-radius:10px;
    background:#ffffff; border:1px solid #e8ecf3;
    font:800 13px/1 Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
    color:#0b1220; min-width:110px; text-align:right;
    box-shadow:0 2px 6px rgba(15,23,42,.05);
  }

  /* футер с кнопками */
  .prizes__footer{ display:grid; grid-template-columns:1fr 1fr; gap:10px; width:100%; margin-top:16px }
  .prizes__btn{ height:44px; border-radius:12px; font-weight:600 }
  .btn.btn--ghost{
    background:#fff; color:#0b1220; border:1px solid #e5e7eb;
    box-shadow:0 8px 24px rgba(15,23,42,.08);
  }
  .btn.btn--ghost:active{ transform:translateY(1px) }
  .btn.btn--primary{
    background:linear-gradient(180deg,#3b82f6 0%, #2563eb 100%) !important;
    color:#fff !important; border:none !important;
    box-shadow:0 10px 28px rgba(37,99,235,.35);
  }
  .btn.btn--primary:active{ transform:translateY(1px) }
  `;
    const tag = document.createElement('style');
    tag.textContent = css;
    document.head.appendChild(tag);
})();

/* ===================== WISH FORM (карточка №3) ===================== */

/** Ключ в localStorage, куда бот/админка может положить актуальную ссылку */
const LS_WISH_FORM_URL = 'rtp_wish_form_url_v1';

/** Базовый URL формы (дефолт) */
const DEFAULT_WISH_FORM_URL = 'https://forms.gle/zsCos8V7rryYhXuj9';

/** Получаем ссылку на форму:
 *  1) ?wishForm=... (в приоритете, удобно для теста)
 *  2) localStorage[LS_WISH_FORM_URL] (бот может записать)
 *  3) DEFAULT_WISH_FORM_URL (по умолчанию)
 */
function getWishFormUrl() {
    const fromQuery = new URLSearchParams(location.search).get('wishForm');
    if (fromQuery) return fromQuery;
    try {
        const fromLS = localStorage.getItem(LS_WISH_FORM_URL);
        if (fromLS) return fromLS;
    } catch {}
    return DEFAULT_WISH_FORM_URL;
}

/** Открытие ссылки корректно в WebApp/браузере */
function openExternalLink(url) {
    // В телеграм-вебаппе используем API, иначе — обычное открытие
    const tg = window.Telegram?.WebApp;
    if (tg?.openLink) {
        tg.openLink(url, { try_instant_view: false });
    } else {
        // в браузере
        window.open(url, '_blank', 'noopener,noreferrer');
    }
}

/** Привязка к кнопке третьей карточки */
(function bindWishCard() {
    // Третья карточка: индекс [2]
    const wishBtn = document.querySelectorAll('.rtp-card')[2]?.querySelector('.rtp-card__btn');
    if (!wishBtn) return;

    wishBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const url = getWishFormUrl();
        openExternalLink(url);
    });
})();
/* =================== /WISH FORM =================== */

