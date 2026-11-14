/* Patchland: language of the pages without a language prefix ("/", "/journal/", "/privacy/" ...; never /xx/ and never 404.html).
   Inlined by build_site, which fills in S (all site languages) and A (the languages that really have THIS page).
   Order: ?lang=xx in the URL > the language saved by the header picker (localStorage "ipe_lang") > first match in
   navigator.languages (the first two letters, zh-CN stays English, zh-TW/HK/MO -> zh-Hant, pt-* -> pt-BR) > stay on the English root.
   Redirect only when the language is not English and A has it; a language URL (/ko/...) is never redirected.
   Crawlers and bots (UA) are never redirected. ?lang=xx (company-wide hand-off): a supported language is saved and the
   page moves to "/xx/<same path>" (en stays, the query is cleaned); an unsupported one is ignored.
   No server redirect: crawlers see "/" as English. */
(function(){
  var S=/*SUPPORTED*/[],A=/*AVAILABLE*/[],K='ipe_lang';
  /* "ko-KR" -> "ko", "zh_TW" -> "zh-Hant" ... first supported match for a language tag, or '' */
  function pick(c){
    c=String(c||'').toLowerCase().replace(/_/g,'-');
    /* legacy codes: Android/old browsers say "in" for Indonesian. Chinese: only Traditional (zh-TW/HK/MO/Hant) is a site language; Simplified is not. */
    var b=c.split('-')[0];
    if(b==='in')b='id';
    if(b==='zh'){var r=c.split('-').slice(1);var hant=r.indexOf('hant')>=0||(r.indexOf('hans')<0&&(r.indexOf('tw')>=0||r.indexOf('hk')>=0||r.indexOf('mo')>=0));return hant&&S.indexOf('zh-Hant')>=0?'zh-Hant':''}
    if(b==='pt')return S.indexOf('pt-BR')>=0?'pt-BR':'';
    return S.indexOf(b)>=0?b:'';
  }
  function saved(){try{return localStorage.getItem(K)||''}catch(e){return ''}}
  function save(v){try{localStorage.setItem(K,v)}catch(e){}}
  try{
    if(/bot|crawl|spider|slurp|lighthouse/i.test(navigator.userAgent||''))return;
    var seg=location.pathname.split('/')[1];
    if(seg&&(S.indexOf(seg)>=0||seg==='pt'||seg==='zh'||seg==='ru'))return;
    var to='',want='',hasLang=false,parts=(location.search||'').replace(/^\?/,'').split('&').filter(Boolean),rest=[];
    for(var j=0;j<parts.length;j++){
      var kv=parts[j].split('=');
      if(kv[0]==='lang'){hasLang=true;if(!want){try{want=pick(decodeURIComponent((kv.slice(1).join('=')||'').replace(/\+/g,' ')))}catch(e){}}}
      else rest.push(parts[j]);
    }
    var clean=location.pathname+(rest.length?'?'+rest.join('&'):'')+location.hash;
    if(want){
      save(want);
      if(want==='en'){if(history.replaceState)history.replaceState(null,'',clean);return}
      to=want;
    }else if(S.indexOf(saved())>=0){
      to=saved();
    }else{
      var L=(navigator.languages&&navigator.languages.length)?navigator.languages:[navigator.language||''];
      for(var i=0;i<L.length&&!to;i++)to=pick(L[i]);
    }
    if(to&&to!=='en'&&A.indexOf(to)>=0)location.replace('/'+to+clean);
    else if(hasLang&&history.replaceState)history.replaceState(null,'',clean);
  }catch(e){}
})();
