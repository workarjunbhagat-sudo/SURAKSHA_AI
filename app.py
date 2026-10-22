import json
import csv
import io
import re
from datetime import datetime
import streamlit as st
from i18n import tr, LANGS
from realtime_ai import dynamic_answer, transcribe_openai, speak_openai
from analyzer import DEMO_MESSAGES
from api_client import analyze_message, analyze_url, api_configured
from ml_engine import METRICS
from ocr_engine import extract_text_from_image, ocr_available

st.set_page_config(page_title='SURAKSHA AI', page_icon='🛡️', layout='wide')
st.markdown("""<style>
.stApp{background:radial-gradient(ellipse at top left,#102b45 0%,#07111f 42%,#050a12 100%);color:#e8f4ff}
.block-container{padding-top:1.2rem;max-width:1480px}
.hero{padding:30px 34px;border-radius:22px;background:linear-gradient(125deg,#07111f 0%,#103b5a 55%,#087e8b 100%);color:white;margin-bottom:22px;box-shadow:0 0 35px rgba(0,203,255,.13);border:1px solid rgba(74,222,255,.28)}
.hero h1{font-size:44px;margin:0;letter-spacing:-1px;color:#f5fbff}.hero p{font-size:18px;color:#bceeff;margin-top:8px}
.risk{padding:20px;border-radius:18px;text-align:center;border:1px solid #244b66;background:linear-gradient(180deg,#10263a,#0a1726);box-shadow:0 0 22px rgba(0,204,255,.08);color:#e8f4ff}
.risk-number{font-size:48px;font-weight:800;letter-spacing:-1px;color:#5ce1ff}
.card,.feature{padding:18px;border-radius:16px;background:linear-gradient(145deg,#10263a,#0a1726);border:1px solid #24465d;margin-bottom:12px;box-shadow:0 6px 22px rgba(0,0,0,.18);color:#e8f4ff}
.feature{min-height:125px}.feature h3{margin-top:0;color:#71e4ff}
.stMarkdown,.stCaption,.stText,.stMetric label{color:#d9eafa}
.stButton>button,.stDownloadButton>button{border-radius:11px;font-weight:700;border:1px solid #2b7795;transition:all .15s ease}
.stButton>button[kind="primary"]{background:linear-gradient(100deg,#087eaa,#00a6a6);color:white}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);box-shadow:0 0 18px rgba(0,210,255,.2);border-color:#55ddff}
.stTabs [data-baseweb="tab-list"]{gap:5px;background:#091827;border:1px solid #1c3b52;border-radius:12px;padding:5px}
.stTabs [data-baseweb="tab"]{border-radius:9px;padding:10px 13px;color:#b8d7e9}
.stTabs [aria-selected="true"]{background:#123b53;color:#6ee7ff;font-weight:750}
.stMetric{background:linear-gradient(145deg,#10263a,#0a1726);border:1px solid #24465d;padding:12px 14px;border-radius:14px;box-shadow:0 3px 16px rgba(0,0,0,.16)}
[data-testid="stSidebar"]{background:#071421;border-right:1px solid #1c3b52}
[data-testid="stSidebar"] *{color:#d9eafa}
.stAlert{border-radius:12px;background:#10263a}
input,textarea,[data-baseweb="select"]>div{background:#0b1b2b!important;color:#e8f4ff!important}
hr{border-color:#24465d}
</style>""", unsafe_allow_html=True)

for key, default in {'demo_text':'','history':[],'last_result':None,'ocr_text':'','ocr_result':None,'last_url_result':None,'chat_history':[],'family_alert':'','quiz_score':0,'quiz_done':False,'language':'English','openai_key':'','batch_results':[]}.items():
    if key not in st.session_state: st.session_state[key]=default

lang=st.session_state.language
# Keep stable internal language values; only the visible labels are translated.
LANGUAGE_DISPLAY = {
    'English': {'English':'English','Hindi':'Hindi','Hinglish':'Hinglish'},
    'हिंदी': {'English':'अंग्रेज़ी','Hindi':'हिंदी','Hinglish':'हिंग्लिश'},
    'Hinglish': {'English':'English','Hindi':'Hindi','Hinglish':'Hinglish'},
}
# Recover safely if an old session contains an invalid language value.
if lang not in LANGS:
    lang = 'English'
    st.session_state.language = lang
with st.sidebar:
    st.markdown('## 🛡️ SURAKSHA AI')
    st.caption(tr(lang,'app_tag'))
    current_index = LANGS.index(lang)
    chosen_internal=st.selectbox(
        tr(lang,'language'),
        LANGS,
        index=current_index,
        format_func=lambda x: LANGUAGE_DISPLAY.get(lang, LANGUAGE_DISPLAY['English']).get(x, x),
        key='language_select'
    )
    if chosen_internal != lang:
        st.session_state.language=chosen_internal
        st.rerun()
    lang=st.session_state.language
    st.divider()
    st.markdown(f'### {tr(lang,"live_ai")}')
    api_key=st.text_input(tr(lang,'api_key'), type='password', value=st.session_state.get('openai_key',''), placeholder='sk-...', help=tr(lang,'web_help'))
    st.session_state.openai_key=api_key
    web_search=st.checkbox(tr(lang,'web_search'), value=False, help=tr(lang,'web_help'))
    if api_key: st.success(tr(lang,'ai_ready'))
    else: st.info(tr(lang,'ai_no_key'))
    st.divider()
    st.markdown(f'### {tr(lang,"demo")}')
    demo_keys=list(DEMO_MESSAGES.keys())
    demo_labels={'English':demo_keys,'हिंदी':['नकली केवाईसी / बैंक संदेश','डिजिटल अरेस्ट शैली','इनाम धोखाधड़ी','कम जोखिम उदाहरण'],'Hinglish':['Fake KYC / bank message','Digital arrest style','Prize scam','Lower-risk example']}
    demo_display=demo_labels[lang]
    selected_demo=st.selectbox(tr(lang,'choose_scenario'), demo_display)
    demo_key=demo_keys[demo_display.index(selected_demo)]
    if st.button(tr(lang,'load_demo'),use_container_width=True):
        st.session_state.demo_text=DEMO_MESSAGES[demo_key]; st.session_state.last_result=None; st.success(tr(lang,'demo_loaded'))
    if st.button(tr(lang,'clear'),use_container_width=True):
        for k,v in [('history',[]),('last_result',None),('ocr_text',''),('ocr_result',None),('last_url_result',None),('chat_history',[]),('batch_results',[]),]: st.session_state[k]=v
        st.rerun()


st.markdown(f'''<div class="hero"><h1>🛡️ SURAKSHA AI</h1><p>{tr(lang,'app_tag')}</p><p style="font-size:14px;opacity:.85">{tr(lang,'voice_enabled')}</p></div>''',unsafe_allow_html=True)

c1,c2,c3,c4=st.columns(4)
for col,title,desc in [(c1,tr(lang,'message'),tr(lang,'card_msg')),(c2,tr(lang,'screenshot'),tr(lang,'card_screen')),(c3,tr(lang,'link'),tr(lang,'card_link')),(c4,tr(lang,'safety'),tr(lang,'card_safe'))]:
    with col: st.markdown(f'<div class="feature"><h3>{title}</h3><div>{desc}</div></div>',unsafe_allow_html=True)

EXTRA_TAB_LABELS = {'English':['📚 Batch Scan','✅ Safety Readiness'],'हिंदी':['📚 बैच स्कैन','✅ सुरक्षा तैयारी'],'Hinglish':['📚 Batch Scan','✅ Safety Readiness']}
tabs=st.tabs([tr(lang,'dashboard'),tr(lang,'message'),tr(lang,'screenshot'),tr(lang,'link'),tr(lang,'model'),tr(lang,'ask'),tr(lang,'safety'),tr(lang,'trainer'),tr(lang,'library'),tr(lang,'history')] + EXTRA_TAB_LABELS[lang])

CATEGORY={
'Bank / KYC scam':{'English':'Bank / KYC scam','हिंदी':'बैंक / केवाईसी धोखाधड़ी','Hinglish':'Bank / KYC scam'},
'Authority / digital-arrest scam':{'English':'Authority / digital-arrest scam','हिंदी':'अधिकारी / डिजिटल अरेस्ट धोखाधड़ी','Hinglish':'Authority / digital-arrest scam'},
'Payment / UPI scam':{'English':'Payment / UPI scam','हिंदी':'भुगतान / यूपीआई धोखाधड़ी','Hinglish':'Payment / UPI scam'},
'Prize / reward scam':{'English':'Prize / reward scam','हिंदी':'इनाम / पुरस्कार धोखाधड़ी','Hinglish':'Prize / reward scam'},
'Job / recruitment scam':{'English':'Job / recruitment scam','हिंदी':'नौकरी / भर्ती धोखाधड़ी','Hinglish':'Job / recruitment scam'},
'Investment scam':{'English':'Investment scam','हिंदी':'निवेश धोखाधड़ी','Hinglish':'Investment scam'},
'Delivery / parcel scam':{'English':'Delivery / parcel scam','हिंदी':'डिलीवरी / पार्सल धोखाधड़ी','Hinglish':'Delivery / parcel scam'},
'Suspicious message':{'English':'Suspicious message','हिंदी':'संदिग्ध संदेश','Hinglish':'Suspicious message'},
'No message':{'English':'No message','हिंदी':'कोई संदेश नहीं','Hinglish':'Koi message nahi'}}
IND={
'Urgency':('Urgency','जल्दी करने का दबाव','Urgency'), 'Threat / fear':('Threat / fear','धमकी / डर','Threat / fear'), 'Sensitive information request':('Sensitive information request','संवेदनशील जानकारी की मांग','Sensitive information request'), 'Suspicious link':('Suspicious link','संदिग्ध लिंक','Suspicious link'), 'Impersonation language':('Impersonation language','किसी संस्था/अधिकारी की नकल','Impersonation language'), 'Payment request':('Payment request','भुगतान की मांग','Payment request'), 'Prize / reward bait':('Prize / reward bait','इनाम / पुरस्कार का लालच','Prize / reward bait')}
EXPL={
'Urgency':{'English':'The message pressures the recipient to act quickly.','हिंदी':'संदेश प्राप्तकर्ता पर जल्दी कार्रवाई करने का दबाव डालता है।','Hinglish':'Message recipient par jaldi action lene ka pressure daalta hai.'},
'Threat / fear':{'English':'It uses fear, punishment or consequences to push a decision.','हिंदी':'यह डर, सजा या परिणाम का इस्तेमाल करके निर्णय लेने का दबाव बनाता है।','Hinglish':'Ye fear, punishment ya consequences use karke decision lene ka pressure banata hai.'},
'Sensitive information request':{'English':'It asks for information that should not be shared through an unsolicited message or call.','हिंदी':'यह ऐसी जानकारी मांगता है जिसे अनचाहे संदेश या कॉल पर साझा नहीं करना चाहिए।','Hinglish':'Ye aisi information maangta hai jo unsolicited message ya call par share nahi karni chahiye.'},
'Suspicious link':{'English':'A link is included; verify the destination independently before opening it.','हिंदी':'एक लिंक दिया गया है; खोलने से पहले उसके गंतव्य की स्वतंत्र रूप से पुष्टि करें।','Hinglish':'Link diya gaya hai; open karne se pehle destination independently verify karo.'},
'Impersonation language':{'English':'The message presents itself as an authority or trusted organization.','हिंदी':'संदेश खुद को किसी अधिकारी या भरोसेमंद संस्था के रूप में पेश करता है।','Hinglish':'Message khud ko authority ya trusted organization ke roop mein present karta hai.'},
'Payment request':{'English':'It asks the recipient to transfer or pay money.','हिंदी':'यह प्राप्तकर्ता से पैसे भेजने या भुगतान करने को कहता है।','Hinglish':'Ye recipient se money transfer ya payment karne ko kehta hai.'},
'Prize / reward bait':{'English':'It uses a prize, reward or cashback claim to encourage action.','हिंदी':'यह कार्रवाई करवाने के लिए इनाम, पुरस्कार या कैशबैक का लालच देता है।','Hinglish':'Ye action karwane ke liye prize, reward ya cashback ka lure use karta hai.'}}
ACTION={'Do not share OTPs, PINs, passwords or CVV.':{'English':'Do not share OTPs, PINs, passwords or CVV.','हिंदी':'ओटीपी, पिन, पासवर्ड या सीवीवी साझा न करें।','Hinglish':'OTP, PIN, password ya CVV share mat karo.'},'Do not click a suspicious link or install an app because of an unsolicited message.':{'English':'Do not click a suspicious link or install an app because of an unsolicited message.','हिंदी':'अनचाहे संदेश के कारण संदिग्ध लिंक पर क्लिक न करें और कोई ऐप इंस्टॉल न करें।','Hinglish':'Unsolicited message ki wajah se suspicious link click ya app install mat karo.'},'Verify the request independently using the organization’s official app, website or contact channel.':{'English':'Verify the request independently using the organization’s official app, website or contact channel.','हिंदी':'संस्था के आधिकारिक ऐप, वेबसाइट या संपर्क माध्यम से अनुरोध की स्वतंत्र रूप से पुष्टि करें।','Hinglish':'Organization ke official app, website ya contact channel se request independently verify karo.'},'If money has already been sent, contact your bank/payment provider immediately and preserve evidence.':{'English':'If money has already been sent, contact your bank/payment provider immediately and preserve evidence.','हिंदी':'अगर पैसे भेजे जा चुके हैं, तो तुरंत बैंक/भुगतान प्रदाता से संपर्क करें और सबूत सुरक्षित रखें।','Hinglish':'Agar money already send ho gaya hai, turant bank/payment provider ko contact karo aur evidence save karo.'}}

def category_name(x): return CATEGORY.get(x,{'English':x,'हिंदी':x,'Hinglish':x}).get(lang,x)
def indicator_name(x): return IND.get(x,(x,x,x))[{'English':0,'हिंदी':1,'Hinglish':2}[lang]]
def indicator_expl(x): return EXPL.get(x,{}).get(lang,x)
def action_text(x): return ACTION.get(x,{}).get(lang,x)

def add_history(source,text,result): st.session_state.history.append({'time':datetime.now().strftime('%d-%m-%Y %H:%M'),'source':source,'risk':result.get('risk',0),'category':result.get('category','Suspicious message'),'summary':result.get('summary',''),'text':text[:500]})

def show_result(result):
    risk=result['risk']; label=tr(lang,'risk_label_high') if risk>=70 else (tr(lang,'risk_label_susp') if risk>=40 else tr(lang,'risk_label_low'))
    a,b=st.columns([1,2])
    with a: st.markdown(f'<div class="risk"><div>{label}</div><div class="risk-number">{risk}/100</div><div>{tr(lang,"indicator_strength")}</div></div>',unsafe_allow_html=True)
    with b:
        st.markdown(f'### {tr(lang,"analysis")}')
        st.markdown(f'**{tr(lang,"category")}:** {category_name(result.get("category","Suspicious message"))}')
        p=result.get('ml_probability',0)*100
        if risk>=70: s=(f'ML model: Suspicious ({p:.0f}% model probability). Multiple explainable indicators support a high-risk assessment.' if lang=='English' else f'ML मॉडल: संदिग्ध ({p:.0f}% मॉडल संभावना)। कई समझने योग्य संकेत उच्च जोखिम आकलन का समर्थन करते हैं.' if lang=='हिंदी' else f'ML model: Suspicious ({p:.0f}% model probability). Multiple explainable indicators high-risk assessment ko support karte hain.')
        elif risk>=40: s=(f'ML model: Suspicious ({p:.0f}% model probability). Some warning signals were detected; verify independently.' if lang=='English' else f'ML मॉडल: संदिग्ध ({p:.0f}% मॉडल संभावना)। कुछ चेतावनी संकेत मिले; स्वतंत्र रूप से पुष्टि करें।' if lang=='हिंदी' else f'ML model: Suspicious ({p:.0f}% model probability). Kuch warning signals mile; independently verify karo.')
        else: s=(f'ML model: Lower risk ({p:.0f}% model probability). Fewer warning signals were detected, but no automated system can guarantee safety.' if lang=='English' else f'ML मॉडल: कम जोखिम ({p:.0f}% मॉडल संभावना)। कम चेतावनी संकेत मिले, लेकिन कोई स्वचालित सिस्टम सुरक्षा की गारंटी नहीं दे सकता।' if lang=='हिंदी' else f'ML model: Lower risk ({p:.0f}% model probability). Kam warning signals mile, lekin koi automated system safety guarantee nahi kar sakta.')
        st.markdown(s); st.caption(f'{tr(lang,"ml_probability")}: {p:.1f}%')
    st.markdown(f'### {tr(lang,"why")}')
    for item in result.get('indicators',[]): st.markdown(f'- **{indicator_name(item["name"])}** — {indicator_expl(item["name"])}')
    st.markdown(f'### {tr(lang,"actions")}')
    for step in result.get('actions',[]): st.markdown(f'- {action_text(step)}')
    st.info(tr(lang,'risk_notice')); risk_breakdown(result)

def risk_breakdown(result):
    st.markdown(f'### {tr(lang,"breakdown")}')
    names={x['name'] for x in result.get('indicators',[])}
    weights={'Urgency':18,'Threat / fear':18,'Sensitive information request':22,'Suspicious link':16,'Impersonation language':12,'Payment request':18,'Prize / reward bait':12}
    rows=[{tr(lang,'signal'):indicator_name(n),tr(lang,'detected'):tr(lang,'yes') if n in names else tr(lang,'no'),tr(lang,'weight'):w if n in names else 0} for n,w in weights.items()]
    st.table(rows); st.caption(tr(lang,'weight_note'))

with tabs[0]:
    st.markdown(f'## {tr(lang,"dashboard")}'); total=len(st.session_state.history); high=sum(x['risk']>=70 for x in st.session_state.history); sus=sum(40<=x['risk']<70 for x in st.session_state.history); avg=sum(x['risk'] for x in st.session_state.history)/total if total else 0
    a,b,c,d=st.columns(4); a.metric(tr(lang,'analyses'),total); b.metric(tr(lang,'high'),high); c.metric(tr(lang,'suspicious'),sus); d.metric(tr(lang,'average'),f'{avg:.0f}/100')
    st.markdown(f'### {tr(lang,"how")}'); st.markdown(f'**{tr(lang,"flow")}**')
    if total:
        st.markdown(f'### {tr(lang,"recent")}')
        for item in reversed(st.session_state.history[-5:]): st.markdown(f'🔴 **{item["source"]}** · {item["risk"]}/100 · {category_name(item["category"])} · {item["time"]}')
        st.markdown(f'### {tr(lang,"category_breakdown")}'); st.bar_chart({category_name(k):sum(1 for x in st.session_state.history if x['category']==k) for k in set(x['category'] for x in st.session_state.history)})
        st.markdown('### Risk distribution')
        risk_counts = {'High (70–100)':sum(1 for x in st.session_state.history if x['risk']>=70),'Review (40–69)':sum(1 for x in st.session_state.history if 40<=x['risk']<70),'Lower (0–39)':sum(1 for x in st.session_state.history if x['risk']<40)}
        st.bar_chart(risk_counts)
        st.caption('Session-only insights. Risk bands are screening indicators, not confirmed fraud cases.')
    else: st.info(tr(lang,'empty_dashboard'))
    st.markdown(f'### {tr(lang,"privacy")}'); st.markdown(tr(lang,'privacy_text'))

with tabs[1]:
    st.markdown(f'## {tr(lang,"check")}'); msg=st.text_area(tr(lang,'paste'),value=st.session_state.demo_text,height=220,placeholder=tr(lang,'placeholder_msg'))
    if st.button(tr(lang,'analyze'),type='primary',use_container_width=True):
        if not msg.strip(): st.warning(tr(lang,'enter_msg'))
        else: r=analyze_message(msg, lang); st.session_state.last_result=r; add_history(tr(lang,'message'),msg,r)
    if st.session_state.last_result: st.divider(); show_result(st.session_state.last_result)

with tabs[2]:
    st.markdown(f'## {tr(lang,"screen_title")}'); st.caption(tr(lang,'screen_caption')); uploaded=st.file_uploader(tr(lang,'upload'),type=['png','jpg','jpeg','webp'],key='screenshot_upload')
    if not ocr_available(): st.warning(tr(lang,'ocr_missing'))
    if uploaded:
        st.image(uploaded,caption=tr(lang,'uploaded'),use_container_width=True)
        if st.button(tr(lang,'extract'),type='primary',use_container_width=True):
            try:
                with st.spinner(tr(lang,'reading')): extracted=extract_text_from_image(uploaded)
                if extracted.strip(): st.session_state.ocr_text=extracted; st.session_state.ocr_result=analyze_message(extracted, lang); add_history(tr(lang,'screenshot'),extracted,st.session_state.ocr_result)
                else: st.error(tr(lang,'no_text'))
            except Exception as e: st.error(str(e))
    if st.session_state.ocr_text:
        st.markdown(f'### {tr(lang,"extracted")}'); st.text_area(tr(lang,'ocr_text'),value=st.session_state.ocr_text,height=180,disabled=True); show_result(st.session_state.ocr_result)

def url_indicator(x):
    m={'Missing URL scheme':('Missing URL scheme','URL योजना गायब है','URL scheme missing hai'),'Obfuscated URL':('Obfuscated URL','छिपा हुआ वेब पता','Obfuscated URL'),'Punycode domain':('Punycode domain','पनीकोड डोमेन','Punycode domain'),'Long domain':('Long domain','बहुत लंबा डोमेन','Long domain'),'IP-address destination':('IP-address destination','IP पते का गंतव्य','IP-address destination'),'Unusual port':('Unusual port','असामान्य पोर्ट','Unusual port'),'Many subdomains':('Many subdomains','कई सबडोमेन','Many subdomains'),'Unencrypted HTTP':('Unencrypted HTTP','एन्क्रिप्शन रहित HTTP','Unencrypted HTTP'),'URL shortener':('URL shortener','URL छोटा करने वाली सेवा','URL shortener'),'Sensitive-action keywords':('Sensitive-action keywords','संवेदनशील कार्रवाई वाले शब्द','Sensitive-action keywords'),'Reserved demo/test domain':('Reserved demo/test domain','आरक्षित डेमो/टेस्ट डोमेन','Reserved demo/test domain'),'Malformed URL':('Malformed URL','गलत संरचना वाला वेब पता','Malformed URL')}; return m.get(x,(x,x,x))[{'English':0,'हिंदी':1,'Hinglish':2}[lang]]
def url_expl(x):
    m={'Missing URL scheme':('The link does not clearly use HTTP or HTTPS.','लिंक में HTTP या HTTPS स्पष्ट रूप से नहीं है।','Link mein HTTP ya HTTPS clearly nahi hai.'),'Obfuscated URL':('The URL contains @, which can hide the actual destination.','URL में @ है, जो असली गंतव्य छिपा सकता है।','URL mein @ hai, jo actual destination hide kar sakta hai.'),'Punycode domain':('The domain uses punycode, which deserves extra verification.','डोमेन पनीकोड का उपयोग करता है, इसलिए अतिरिक्त पुष्टि जरूरी है।','Domain punycode use karta hai, isliye extra verification zaroori hai.'),'Long domain':('An unusually long domain can be a warning sign.','बहुत लंबा डोमेन चेतावनी संकेत हो सकता है।','Unusually long domain warning sign ho sakta hai.'),'IP-address destination':('The link points directly to an IP address instead of a normal domain name.','लिंक सामान्य डोमेन के बजाय सीधे IP पते पर जाता है।','Link normal domain ke bajay directly IP address par jaata hai.'),'Unusual port':('The URL uses a non-standard web port and should be verified independently.','URL गैर-मानक वेब पोर्ट का उपयोग करता है; स्वतंत्र रूप से पुष्टि करें।','URL non-standard web port use karta hai; independently verify karo.'),'Many subdomains':('Multiple nested subdomains can make a destination harder to verify.','कई सबडोमेन गंतव्य की पुष्टि कठिन बना सकते हैं।','Multiple subdomains destination verify karna difficult bana sakte hain.'),'Unencrypted HTTP':('The link does not use HTTPS. Do not treat this alone as proof of fraud.','लिंक HTTPS का उपयोग नहीं करता। इसे अकेले धोखाधड़ी का प्रमाण न मानें।','Link HTTPS use nahi karta. Isse alone fraud ka proof mat samjho.'),'URL shortener':('A shortened link hides the final destination, so verify it before opening.','छोटा किया गया लिंक अंतिम गंतव्य छिपाता है; खोलने से पहले पुष्टि करें।','Shortened link final destination hide karta hai; open karne se pehle verify karo.'),'Sensitive-action keywords':('The URL contains words commonly used in unsolicited verification or reward links.','URL में ऐसे शब्द हैं जो अनचाहे सत्यापन या इनाम लिंक में आम हैं।','URL mein words hain jo unsolicited verification ya reward links mein common hote hain.'),'Reserved demo/test domain':('This is a reserved domain used for examples or testing.','यह उदाहरण या परीक्षण के लिए आरक्षित डोमेन है।','Ye examples ya testing ke liye reserved domain hai.'),'Malformed URL':('The URL could not be parsed normally.','वेब पते को सामान्य रूप से पढ़ा नहीं जा सका।','URL normal tarah se parse nahi ho saka.')}; return m.get(x,(x,x,x))[{'English':0,'हिंदी':1,'Hinglish':2}[lang]]

with tabs[3]:
    st.markdown(f'## {tr(lang,"link_title")}'); url=st.text_input(tr(lang,'url_label'),placeholder=tr(lang,'url_placeholder'))
    if st.button(tr(lang,'check_link'),use_container_width=True):
        if not url.strip(): st.warning(tr(lang,'enter_url'))
        else:
            r=analyze_url(url, lang); st.session_state.last_url_result=r
            msg= (f'{tr(lang,"risk_label_high")} — {r["risk"]}/100' if r['risk']>=70 else f'{tr(lang,"risk_label_susp")} — {r["risk"]}/100' if r['risk']>=40 else f'{tr(lang,"risk_label_low")} — {r["risk"]}/100')
            (st.error if r['risk']>=70 else st.warning if r['risk']>=40 else st.success)(msg)
            for x in r['indicators']: st.markdown(f'- **{url_indicator(x["name"])}** — {url_expl(x["name"])}')
            st.caption(tr(lang,'url_note'))


with tabs[4]:
    st.markdown(f'## {tr(lang,"model_title")}'); st.caption(tr(lang,'model_caption')); c1,c2,c3,c4=st.columns(4); c1.metric(tr(lang,'accuracy'),f'{METRICS["accuracy"]*100:.1f}%'); c2.metric(tr(lang,'precision'),f'{METRICS["precision"]*100:.1f}%'); c3.metric(tr(lang,'recall'),f'{METRICS["recall"]*100:.1f}%'); c4.metric(tr(lang,'f1'),f'{METRICS["f1"]*100:.1f}%')
    st.markdown(f'<div class="card"><b>{tr(lang,"training")}:</b> {METRICS["train_samples"]} &nbsp; | &nbsp; <b>{tr(lang,"testing")}:</b> {METRICS["test_samples"]}<br><br><b>{tr(lang,"pipeline")}:</b> TF-IDF → Logistic Regression → Probability + Explainable Rule Fusion</div>',unsafe_allow_html=True)
    cm=METRICS['confusion_matrix']; st.markdown(f'### {tr(lang,"confusion")}'); st.table({'': [tr(lang,'actual_lower'),tr(lang,'actual_susp')],tr(lang,'pred_lower'):[cm[0][0],cm[1][0]],tr(lang,'pred_susp'):[cm[0][1],cm[1][1]]}); st.warning(tr(lang,'model_note'))

with tabs[5]:
    st.markdown(f'## {tr(lang,"ask_title")}'); st.caption(tr(lang,'ask_caption')); mode=st.radio(tr(lang,'input_mode'),[tr(lang,'type'),tr(lang,'voice')],horizontal=True)
    if st.session_state.chat_history:
        st.markdown(f'### {tr(lang,"conversation")}')
        for h in st.session_state.chat_history[-6:]: st.markdown(f'**{("👤 "+tr(lang,"you")) if h["role"]=="user" else ("🛡️ "+tr(lang,"suraksha"))}:** {h["content"]}')
    if mode==tr(lang,'voice'):
        if not st.session_state.openai_key: st.warning(tr(lang,'need_key'))
        audio=st.audio_input(tr(lang,'speak'))
        if audio:
            st.audio(audio)
            if st.button(tr(lang,'voice_process'),type='primary',use_container_width=True):
                try:
                    with st.spinner(tr(lang,'listening')): q=transcribe_openai(audio,lang,st.session_state.openai_key)
                    st.markdown(f'**{tr(lang,"you_said")}:** {q}')
                    with st.spinner(tr(lang,'thinking')): reply,provider=dynamic_answer(q,lang,st.session_state.openai_key,'',web_search,st.session_state.chat_history)
                    st.session_state.chat_history += [{'role':'user','content':q},{'role':'assistant','content':reply}]; st.success(reply); st.caption(f'{tr(lang,"ai_engine")}: {provider}')
                    with st.spinner(tr(lang,'voice_prep')): path=speak_openai(reply,lang,st.session_state.openai_key)
                    st.audio(path,format='audio/mp3'); st.caption(tr(lang,'voice_clear'))
                except Exception as e: st.error(f'{tr(lang,"voice_error")}: {e}')
    else:
        q=st.text_area(tr(lang,'ask_text_label'),height=140,placeholder=tr(lang,'ask_placeholder')); ca,cb=st.columns([4,1])
        with ca: ask_now=st.button(tr(lang,'ask_live'),type='primary',use_container_width=True)
        with cb:
            if st.button(tr(lang,'clear_chat'),use_container_width=True): st.session_state.chat_history=[]; st.rerun()
        if ask_now:
            if not q.strip(): st.warning(tr(lang,'type_question'))
            else:
                try:
                    with st.spinner(tr(lang,'thinking')): reply,provider=dynamic_answer(q,lang,st.session_state.openai_key,'',web_search,st.session_state.chat_history)
                    st.session_state.chat_history += [{'role':'user','content':q},{'role':'assistant','content':reply}]; st.success(reply); st.caption(f'{tr(lang,"ai_engine")}: {provider}')
                    if st.session_state.openai_key:
                        with st.spinner(tr(lang,'voice_prep')): path=speak_openai(reply,lang,st.session_state.openai_key)
                        st.audio(path,format='audio/mp3'); st.caption(tr(lang,'voice_clear'))
                except Exception as e: st.error(f'{tr(lang,"voice_error")}: {e}')

with tabs[6]:
    st.markdown(f'## {tr(lang,"safety_title")}'); st.markdown(f'### {tr(lang,"scammed")}'); st.markdown(f'<div class="card"><b>{tr(lang,"pause_box")}</b></div>',unsafe_allow_html=True)
    for x in tr(lang,'safety_steps'): st.markdown(f'- {x}')
    st.markdown(f'### {tr(lang,"family")}'); alert_name=st.text_input(tr(lang,'person'),placeholder=tr(lang,'person_placeholder')); alert_type=st.selectbox(tr(lang,'situation'),tr(lang,'incidents'))
    if st.button(tr(lang,'generate_alert')):
        st.session_state.family_alert=f'{tr(lang,"family")}\n\n{tr(lang,"person")}: {alert_name or ("परिवार का सदस्य" if lang=="हिंदी" else "Family member" if lang=="English" else "Family member")}\n{tr(lang,"situation")}: {alert_type}\n\n{tr(lang,"risk_notice")}'
    if st.session_state.family_alert: st.text_area(tr(lang,'copy_alert'),st.session_state.family_alert,height=190)
    st.markdown(f'### {tr(lang,"incident")}'); incident=st.selectbox(tr(lang,'what_happened'),tr(lang,'incidents'))
    for step in tr(lang,'incident_steps')[incident]: st.markdown(f'- {step}')
    st.markdown(f'### {tr(lang,"call_check")}'); score=sum(st.checkbox(x,key=f'call_{i}') for i,x in enumerate(tr(lang,'checks')))
    if score>=3: st.error(f'🔴 {score}/5 {tr(lang,"warning")}')
    elif score: st.warning(f'🟠 {score}/5 {tr(lang,"verify")}')
    else: st.success(f'🟢 {tr(lang,"none")}')
    st.markdown(f'### {tr(lang,"expo")}')
    for x in tr(lang,'expo_items'): st.checkbox(x,key='expo_'+x)

SCENARIOS={
'English':[
('A caller says: “I am from your bank. Tell me the OTP so I can stop a fraudulent transaction.” What should you do?',['Share the OTP quickly','Hang up and contact the bank through its official channel','Ask the caller for their employee ID and then share it'],1,'Banks and legitimate support channels should not require you to disclose an OTP to an unsolicited caller. Verify independently.'),
('A message says you won ₹50,000 but must pay ₹499 first. What is the safer response?',['Pay the ₹499','Send your OTP first','Do not pay; independently verify the claim'],2,'Unexpected prize claims combined with upfront fees are a common warning pattern.'),
('Someone claiming to be an official demands a money transfer during a video call and threatens arrest. What should you do?',['Transfer immediately','Pause and verify the claim through an official channel','Keep the call secret and follow instructions'],1,'Fear and urgency can pressure people into unsafe decisions. Independent verification is safer.'),
('A refund message asks for your card CVV and OTP. What should you do?',['Share both','Share only the CVV','Do not share them and verify the refund independently'],2,'CVV and OTP are sensitive credentials and should not be disclosed to unsolicited contacts.'),
('A delivery message contains an unexpected payment link. What is the best first step?',['Click immediately','Verify the delivery in the official app/site','Forward it to everyone'],1,'Verify the parcel independently rather than trusting an unexpected payment link.')],
'हिंदी':[
('एक कॉल करने वाला कहता है: “मैं आपके बैंक से हूं। धोखाधड़ी वाला लेन-देन रोकने के लिए ओटीपी बताइए।” आपको क्या करना चाहिए?',['ओटीपी तुरंत बता दें','कॉल काटें और आधिकारिक माध्यम से बैंक से संपर्क करें','कॉलर की कर्मचारी आईडी पूछकर ओटीपी बता दें'],1,'अनचाहे कॉल पर बैंक या वैध सहायता सेवा को ओटीपी बताने की जरूरत नहीं होनी चाहिए। स्वतंत्र रूप से पुष्टि करें।'),
('संदेश कहता है कि आपने ₹50,000 जीते हैं लेकिन पहले ₹499 देने होंगे। सुरक्षित प्रतिक्रिया क्या है?',['₹499 दे दें','पहले ओटीपी भेजें','भुगतान न करें; दावे की स्वतंत्र रूप से पुष्टि करें'],2,'अचानक मिलने वाले इनाम के साथ पहले शुल्क मांगना चेतावनी संकेत हो सकता है।'),
('कोई अधिकारी होने का दावा करके वीडियो कॉल पर गिरफ्तारी की धमकी देता है और पैसे भेजने को कहता है। क्या करें?',['तुरंत पैसे भेजें','रुकें और आधिकारिक माध्यम से दावे की पुष्टि करें','कॉल गुप्त रखें और निर्देश मानें'],1,'डर और जल्दी का दबाव असुरक्षित निर्णय करवाने के लिए इस्तेमाल हो सकता है। स्वतंत्र पुष्टि सुरक्षित कदम है।'),
('रिफंड संदेश कार्ड सीवीवी और ओटीपी मांगता है। क्या करें?',['दोनों साझा करें','केवल सीवीवी साझा करें','साझा न करें और रिफंड की स्वतंत्र पुष्टि करें'],2,'सीवीवी और ओटीपी संवेदनशील जानकारी हैं और अनचाहे संपर्कों को नहीं देनी चाहिए।'),
('डिलीवरी संदेश में अचानक भुगतान लिंक है। पहला कदम क्या होना चाहिए?',['तुरंत क्लिक करें','आधिकारिक ऐप/वेबसाइट में डिलीवरी की पुष्टि करें','सबको फॉरवर्ड करें'],1,'अनपेक्षित भुगतान लिंक पर भरोसा करने के बजाय पार्सल की स्वतंत्र पुष्टि करें।')],
'Hinglish':[
('Caller bolta hai: “Main aapke bank se hoon. Fraud transaction rokne ke liye OTP batao.” Kya karna chahiye?',['OTP jaldi share karo','Call cut karke official channel se bank ko contact karo','Employee ID poochkar OTP share karo'],1,'Unsolicited caller ko OTP dene ki zarurat nahi honi chahiye. Independently verify karo.'),
('Message bolta hai ki aap ₹50,000 jeet gaye ho, lekin pehle ₹499 pay karne honge. Safer response kya hai?',['₹499 pay karo','Pehle OTP bhejo','Pay mat karo; claim independently verify karo'],2,'Unexpected prize ke saath upfront fee common warning pattern hai.'),
('Koi official hone ka claim karke video call par arrest ki threat deta hai aur money transfer maangta hai. Kya karo?',['Turant transfer karo','Pause karo aur official channel se verify karo','Call secret rakho aur instructions follow karo'],1,'Fear aur urgency unsafe decision ke liye pressure bana sakte hain. Independent verification safer hai.'),
('Refund message card CVV aur OTP maangta hai. Kya karo?',['Dono share karo','Sirf CVV share karo','Share mat karo aur refund independently verify karo'],2,'CVV aur OTP sensitive credentials hain; unsolicited contacts ko nahi dene chahiye.'),
('Delivery message mein unexpected payment link hai. Best first step kya hai?',['Turant click karo','Official app/site mein delivery verify karo','Sabko forward karo'],1,'Unexpected payment link trust karne ke bajay delivery independently verify karo.')]
}
with tabs[7]:
    st.markdown(f'## {tr(lang,"trainer_title")}'); st.caption(tr(lang,'trainer_caption')); scenarios=SCENARIOS[lang]
    if 'quiz_answers' not in st.session_state: st.session_state.quiz_answers={}
    for i,(q,opts,ans,why) in enumerate(scenarios):
        st.markdown(f'### {i+1}. {q}'); choice=st.radio(tr(lang,'safer'),opts,key=f'quiz_{i}'); st.session_state.quiz_answers[i]=opts.index(choice)
    if st.button(tr(lang,'check_score'),type='primary',use_container_width=True): st.session_state.quiz_score=sum(st.session_state.quiz_answers.get(i)==s[2] for i,s in enumerate(scenarios)); st.session_state.quiz_done=True
    if st.session_state.quiz_done:
        st.metric(tr(lang,'score'),f'{st.session_state.quiz_score}/5'); s=st.session_state.quiz_score
        st.success(tr(lang,'excellent') if s==5 else tr(lang,'good') if s>=3 else tr(lang,'practice')); st.markdown(f'### {tr(lang,"learning")}'); st.markdown(f'**{tr(lang,"learning_line")}**')

with tabs[8]:
    st.markdown(f'## {tr(lang,"library")}')
    library={'Bank / KYC scam':('🏦 Bank / KYC','KYC, account block ya sensitive information request. OTP/PIN/CVV, unknown links aur threats warning signs hain.'),'Authority / digital-arrest scam':('👮 Digital arrest / authority','Police, court ya cyber officer hone ka claim karke money ya sensitive information maangna.'),'Payment / UPI scam':('💳 UPI / payment','Refund, collect request ya OTP maangne wale payment messages.'),'Prize / reward scam':('🎁 Prize / lottery','Unexpected prize jisme pehle fee, bank details ya OTP maanga jaye.'),'Job / recruitment scam':('💼 Job scam','Job offer jisme registration, deposit ya joining se pehle payment maanga jaye.'),'Delivery / parcel scam':('📦 Courier / customs','Parcel, customs ya delivery fail hone ke naam par unexpected payment links.'),'Investment scam':('📈 Investment scam','Guaranteed profit ya turant investment deposit ka pressure.')}
    for k,(title,desc) in library.items():
        if lang=='हिंदी': title,desc={'Bank / KYC scam':('🏦 बैंक / केवाईसी','केवाईसी, खाता बंद होने या संवेदनशील जानकारी की मांग। ओटीपी/पिन/सीवीवी, अनजान लिंक और धमकी चेतावनी संकेत हैं।'),'Authority / digital-arrest scam':('👮 डिजिटल अरेस्ट / अधिकारी','पुलिस, अदालत या साइबर अधिकारी होने का दावा करके पैसे या संवेदनशील जानकारी मांगना।'),'Payment / UPI scam':('💳 यूपीआई / भुगतान','रिफंड, कलेक्ट अनुरोध या ओटीपी मांगने वाले भुगतान संदेश।'),'Prize / reward scam':('🎁 इनाम / लॉटरी','अचानक मिलने वाला इनाम जिसमें पहले शुल्क, बैंक विवरण या ओटीपी मांगा जाए।'),'Job / recruitment scam':('💼 नौकरी धोखाधड़ी','नौकरी के नाम पर पंजीकरण, जमा या जॉइनिंग से पहले भुगतान मांगना।'),'Delivery / parcel scam':('📦 कूरियर / सीमा शुल्क','पार्सल या डिलीवरी के नाम पर अनपेक्षित भुगतान लिंक।'),'Investment scam':('📈 निवेश धोखाधड़ी','गारंटीड लाभ या तुरंत निवेश जमा करने का दबाव।')}[k]
        elif lang=='Hinglish': title,desc={'Bank / KYC scam':('🏦 Bank / KYC','KYC, account block ya sensitive info request. OTP/PIN/CVV, unknown links aur threats warning signs hain.'),'Authority / digital-arrest scam':('👮 Digital arrest / authority','Police, court ya cyber officer hone ka claim karke money ya sensitive info maangna.'),'Payment / UPI scam':('💳 UPI / payment','Refund, collect request ya OTP maangne wale payment messages.'),'Prize / reward scam':('🎁 Prize / lottery','Unexpected prize jisme pehle fee, bank details ya OTP maanga jaye.'),'Job / recruitment scam':('💼 Job scam','Job offer jisme registration, deposit ya joining se pehle payment maanga jaye.'),'Delivery / parcel scam':('📦 Courier / customs','Parcel ya delivery ke naam par unexpected payment links.'),'Investment scam':('📈 Investment scam','Guaranteed profit ya turant investment deposit ka pressure.')}[k]
        with st.expander(title): st.write(desc)

with tabs[9]:
    st.markdown(f'## {tr(lang,"history_title")}')
    if not st.session_state.history: st.info(tr(lang,'no_history'))
    else:
        for i,item in enumerate(reversed(st.session_state.history),1): st.markdown(f'**{i}. {item["time"]} — {item["source"]} — {item["risk"]}/100 — {category_name(item["category"])}**'); st.caption(item['text'])
    report_lines=[tr(lang,'report_title'),f'{tr(lang,"generated")}: {datetime.now().strftime("%d-%m-%Y %H:%M")}','']
    for item in st.session_state.history: report_lines += [f'{item["time"]} | {item["source"]} | {item["risk"]}/100 | {category_name(item["category"])}',item['text'],'']
    st.download_button(tr(lang,'download_report'),'\n'.join(report_lines),'suraksha_session_report.txt','text/plain',use_container_width=True)
    st.download_button(tr(lang,'export_json'),json.dumps(st.session_state.history,ensure_ascii=False,indent=2),'suraksha_analysis_history.json','application/json',use_container_width=True)

with tabs[10]:
    ui = {
        'English': {'title':'Batch message scanner','caption':'Scan a set of sample messages in one run. Useful for demos and pattern review—not a final fraud decision.','load_demo':'Load demo batch','mode':'Choose input method','modes':['Paste multiple messages','Upload CSV file'],'paste':'Messages to scan','placeholder':'Message 1\n---\nMessage 2\n---\nMessage 3','separator':'Separate messages with a line containing only --- (three dashes).','upload':'Upload CSV','column':'Select the message-text column','run':'Scan messages','empty':'Add at least one non-empty message first.','limit':'For a responsive demo, scan at most 100 messages at a time.','results':'Batch results','all':'All risk levels','high':'High risk (70+)','review':'Needs review (40–69)','low':'Lower risk (0–39)','filter':'Filter results','count':'Messages scanned','highcount':'High risk','reviewcount':'Needs review','export':'Include full message text in downloaded CSV (off by default)','download':'Download batch results (CSV)','privacy':'Messages go to the configured SURAKSHA analysis endpoint when enabled, otherwise they are analyzed locally. Recent text is also kept in this Streamlit session history. Full-text exports may contain sensitive data; use synthetic/demo messages whenever possible.','preview':'Message preview','risk':'Risk','category':'Category','signals':'Signals','band':'Risk band','done':'Scan complete. Results are available below.'},
        'हिंदी': {'title':'कई संदेशों का एक साथ स्कैन','caption':'डेमो और पैटर्न देखने के लिए एक साथ कई नमूना संदेश जांचें। यह अंतिम धोखाधड़ी निर्णय का विकल्प नहीं है।','load_demo':'डेमो संदेश लोड करें','mode':'इनपुट का तरीका चुनें','modes':['कई संदेश पेस्ट करें','CSV फ़ाइल अपलोड करें'],'paste':'जांचने के लिए संदेश','placeholder':'संदेश 1\n---\nसंदेश 2\n---\nसंदेश 3','separator':'हर संदेश के बीच केवल --- वाली अलग लाइन रखें।','upload':'CSV अपलोड करें','column':'संदेश वाले कॉलम को चुनें','run':'संदेश स्कैन करें','empty':'पहले कम से कम एक गैर-खाली संदेश जोड़ें।','limit':'एक बार में अधिकतम 100 संदेश स्कैन करें।','results':'स्कैन परिणाम','all':'सभी जोखिम स्तर','high':'उच्च जोखिम (70+)','review':'जांच जरूरी (40–69)','low':'कम जोखिम (0–39)','filter':'परिणाम फ़िल्टर करें','count':'स्कैन किए संदेश','highcount':'उच्च जोखिम','reviewcount':'जांच जरूरी','export':'डाउनलोड CSV में पूरा संदेश शामिल करें (डिफ़ॉल्ट रूप से बंद)','download':'परिणाम CSV डाउनलोड करें','privacy':'API configured होने पर messages configured SURAKSHA endpoint पर जाते हैं; अन्यथा local analysis होता है। Recent text इस Streamlit session history में रहता है। Full-text export में sensitive data हो सकता है, इसलिए demo messages prefer करें।','preview':'संदेश का अंश','risk':'जोखिम','category':'श्रेणी','signals':'संकेत','band':'जोखिम स्तर','done':'स्कैन पूरा हुआ। परिणाम नीचे हैं।'},
        'Hinglish': {'title':'Batch message scanner','caption':'Demo aur pattern review ke liye multiple sample messages ek saath scan karo. Ise final fraud decision ke liye akela use mat karo.','load_demo':'Demo batch load karo','mode':'Input method choose karo','modes':['Multiple messages paste karo','CSV file upload karo'],'paste':'Scan karne wale messages','placeholder':'Message 1\n---\nMessage 2\n---\nMessage 3','separator':'Har message ke beech separate line mein sirf --- likho.','upload':'CSV upload karo','column':'Message-text column select karo','run':'Messages scan karo','empty':'Pehle kam se kam ek non-empty message add karo.','limit':'Ek baar mein max 100 messages scan karo.','results':'Batch results','all':'All risk levels','high':'High risk (70+)','review':'Review needed (40–69)','low':'Lower risk (0–39)','filter':'Results filter karo','count':'Messages scanned','highcount':'High risk','reviewcount':'Review needed','export':'Downloaded CSV mein full message text include karo (default off)','download':'Batch results CSV download karo','privacy':'API configured hai to messages configured SURAKSHA endpoint par jaate hain; warna local analysis hota hai. Recent text Streamlit session history mein bhi rehta hai. Full-text export mein sensitive data ho sakta hai, isliye demo messages prefer karo.','preview':'Message preview','risk':'Risk','category':'Category','signals':'Signals','band':'Risk band','done':'Scan complete. Results neeche hain.'}
    }[lang]
    st.markdown(f'## {ui["title"]}')
    st.caption(ui['caption'])
    st.info('🛡️ ' + ui['privacy'])
    if st.button(ui['load_demo'], key='load_batch_demo'):
        st.session_state.batch_input_text = DEMO_MESSAGES['Fake KYC / bank message'] + '\n---\n' + DEMO_MESSAGES['Digital arrest style'] + '\n---\n' + DEMO_MESSAGES['Prize scam']
        st.session_state.batch_mode_select = ui['modes'][0]
        st.session_state.batch_results = []
        st.rerun()
    mode = st.radio(ui['mode'], ui['modes'], horizontal=True, key='batch_mode_select')
    batch_items = []
    if mode == ui['modes'][0]:
        pasted = st.text_area(ui['paste'], height=220, placeholder=ui['placeholder'], key='batch_input_text')
        st.caption(ui['separator'])
        batch_items = [part.strip() for part in re.split(r'(?m)^\s*---+\s*$', pasted) if part.strip()]
    else:
        batch_file = st.file_uploader(ui['upload'], type=['csv'], key='batch_upload_csv')
        if batch_file is not None:
            try:
                reader = csv.DictReader(io.StringIO(batch_file.getvalue().decode('utf-8-sig')))
                csv_rows = list(reader)
                headers = list(reader.fieldnames or [])
                if headers:
                    preferred = {'message','text','content','body','sms','email'}
                    default_col = next((i for i, h in enumerate(headers) if h.strip().lower() in preferred), 0)
                    chosen_col = st.selectbox(ui['column'], headers, index=default_col, key='batch_csv_text_column')
                    batch_items = [str(row.get(chosen_col, '') or '').strip() for row in csv_rows if str(row.get(chosen_col, '') or '').strip()]
                else:
                    st.warning('CSV header row not found.')
            except (UnicodeDecodeError, csv.Error) as exc:
                st.error(f'Could not read CSV: {exc}')
    if batch_items:
        st.caption(f'{len(batch_items)} non-empty message(s) detected.')
    x, y = st.columns([3, 1])
    with x:
        run_batch = st.button(ui['run'], type='primary', use_container_width=True, key='run_batch_scan')
    with y:
        if st.button(tr(lang, 'clear'), use_container_width=True, key='clear_batch_results'):
            st.session_state.batch_results = []
            st.rerun()
    if run_batch:
        if not batch_items:
            st.warning(ui['empty'])
        elif len(batch_items) > 100:
            st.warning(ui['limit'])
        else:
            new_results = []
            progress = st.progress(0, text='Preparing scan…')
            for idx, msg_text in enumerate(batch_items, start=1):
                try:
                    res = analyze_message(msg_text, lang)
                    risk = int(res.get('risk', 0))
                    row = {'sample': idx, 'message': msg_text, 'risk': risk,
                           'risk_band': 'High' if risk >= 70 else ('Review' if risk >= 40 else 'Lower'),
                           'category': res.get('category', 'Suspicious message'),
                           'signal_count': len(res.get('indicators', []))}
                    new_results.append(row)
                    add_history('Batch scan', msg_text, res)
                except Exception:
                    new_results.append({'sample': idx, 'message': msg_text, 'risk': 0, 'risk_band': 'Error', 'category': 'Analysis unavailable', 'signal_count': 0})
                progress.progress(idx / len(batch_items), text=f'Analyzing {idx} of {len(batch_items)}…')
            st.session_state.batch_results = new_results
            progress.empty()
            st.success(ui['done'])
    if st.session_state.batch_results:
        rows = st.session_state.batch_results
        high_n = sum(r['risk_band'] == 'High' for r in rows)
        review_n = sum(r['risk_band'] == 'Review' for r in rows)
        low_n = sum(r['risk_band'] == 'Lower' for r in rows)
        a, b, c, d = st.columns(4)
        a.metric(ui['count'], len(rows)); b.metric(ui['highcount'], high_n); c.metric(ui['reviewcount'], review_n); d.metric(ui['low'], low_n)
        choice = st.selectbox(ui['filter'], [ui['all'], ui['high'], ui['review'], ui['low']], key='batch_risk_filter')
        band_filter = {ui['all']: None, ui['high']: 'High', ui['review']: 'Review', ui['low']: 'Lower'}[choice]
        visible = [r for r in rows if band_filter is None or r['risk_band'] == band_filter]
        view = [{'#':r['sample'], ui['preview']:r['message'][:100] + ('…' if len(r['message']) > 100 else ''), ui['risk']:r['risk'], ui['band']:r['risk_band'], ui['category']:category_name(r['category']), ui['signals']:r['signal_count']} for r in visible]
        st.dataframe(view, use_container_width=True, hide_index=True)
        include_text = st.checkbox(ui['export'], value=False, key='batch_export_full_text')
        buffer = io.StringIO()
        fields = ['sample','risk','risk_band','category','signal_count'] + (['message'] if include_text else [])
        writer = csv.DictWriter(buffer, fieldnames=fields); writer.writeheader()
        for r in visible: writer.writerow({k:r.get(k,'') for k in fields})
        st.download_button(ui['download'], data=buffer.getvalue().encode('utf-8-sig'), file_name='suraksha_batch_results.csv', mime='text/csv', use_container_width=True)
        st.caption('A risk score is a screening signal—not a calibrated probability or proof that a message is fraudulent or safe.')

with tabs[11]:
    ready = {
        'English': {'title':'Personal digital-safety readiness','caption':'A self-reported checklist for building safer habits; not a security audit.','items':['I use unique passwords for important accounts.','I have enabled multi-factor authentication where available.','I know how to contact my bank through an independently verified channel.','I never share OTPs, PINs, passwords, or CVV with callers/messages.','My phone and apps receive security updates.','I know how to report suspected cyber fraud in my region.'],'heading':'Readiness checklist','download':'Download my checklist','tips_heading':'Remember the STOP check','tips':['Stop before acting on urgency or threats.','Take no action through an unsolicited link or caller.','Open the official app/site yourself and verify independently.'],'disclaimer':'Completion reflects your answers only; it does not measure actual device or account security.'},
        'हिंदी': {'title':'व्यक्तिगत डिजिटल सुरक्षा तैयारी','caption':'सुरक्षित आदतों के लिए स्वयं भरी जाने वाली चेकलिस्ट; यह सुरक्षा ऑडिट नहीं है।','items':['मैं महत्वपूर्ण खातों के लिए अलग-अलग पासवर्ड इस्तेमाल करता/करती हूं।','जहां उपलब्ध है, मैंने मल्टी-फैक्टर प्रमाणीकरण चालू किया है।','मुझे बैंक से आधिकारिक और स्वतंत्र रूप से सत्यापित माध्यम से संपर्क करना आता है।','मैं कॉल/संदेश पर ओटीपी, पिन, पासवर्ड या सीवीवी साझा नहीं करता/करती।','मेरे फोन और ऐप सुरक्षा अपडेट लेते हैं।','मुझे अपने क्षेत्र में साइबर धोखाधड़ी की रिपोर्ट करने का तरीका पता है।'],'heading':'सुरक्षा चेकलिस्ट','download':'मेरी चेकलिस्ट डाउनलोड करें','tips_heading':'STOP जांच याद रखें','tips':['जल्दी या धमकी में आकर तुरंत कार्रवाई न करें।','अनजान लिंक या कॉल के निर्देश पर कार्रवाई न करें।','आधिकारिक ऐप/वेबसाइट खुद खोलकर स्वतंत्र पुष्टि करें।'],'disclaimer':'चेकलिस्ट केवल आपके उत्तर दिखाती है; यह डिवाइस या खाते की वास्तविक सुरक्षा नहीं मापती।'},
        'Hinglish': {'title':'Personal digital-safety readiness','caption':'Safe habits ke liye self-reported checklist; ye security audit nahi hai.','items':['Main important accounts ke liye unique passwords use karta/karti hoon.','Jahan available hai, maine multi-factor authentication enable kiya hai.','Mujhe bank ke independently verified channel se contact karna aata hai.','Main call/message par OTP, PIN, password ya CVV share nahi karta/karti.','Mere phone aur apps security updates receive karte hain.','Mujhe apne region mein suspected cyber fraud report karna aata hai.'],'heading':'Readiness checklist','download':'Meri checklist download karo','tips_heading':'STOP check yaad rakho','tips':['Urgency ya threats par turant action lene se ruko.','Unsolicited link ya caller ke through action mat lo.','Official app/site khud open karke independently verify karo.'],'disclaimer':'Checklist tumhare answers dikhati hai; actual device/account security measure nahi karti.'}
    }[lang]
    st.markdown(f'## {ready["title"]}'); st.caption(ready['caption']); st.markdown(f'### {ready["heading"]}')
    completed = 0
    for idx, item_label in enumerate(ready['items']): completed += int(st.checkbox(item_label, key=f'readiness_item_{idx}'))
    ratio = completed / len(ready['items']); st.progress(ratio, text=f'{completed}/{len(ready["items"])} completed')
    if completed == len(ready['items']): st.success('Great work! Review these habits whenever your apps or accounts change.')
    elif completed >= 4: st.info('Good progress. Choose one unchecked item and complete it today.')
    else: st.warning('Start with unique passwords, multi-factor authentication, and never sharing OTPs.')
    st.markdown(f'### {ready["tips_heading"]}')
    for tip in ready['tips']: st.markdown(f'- {tip}')
    lines = [ready['title'], '', f'Completed: {completed}/{len(ready["items"])}', '']
    for idx, label in enumerate(ready['items']): lines.append(f'[{"x" if st.session_state.get(f"readiness_item_{idx}", False) else " "}] {label}')
    st.download_button(ready['download'], '\n'.join(lines), file_name='suraksha_safety_readiness.txt', mime='text/plain', use_container_width=True)
    st.caption(ready['disclaimer'])

st.divider(); st.caption(tr(lang,'footer'))
