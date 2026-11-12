/* Patchland: language of every page without a language prefix ("/", never /xx/ and never 404.html).
   Inlined by build_site, which fills in S (all site languages) and A (the languages that really have THIS page).
   Order: ?lang=xx in the URL > the language the visitor picked on the site (localStorage "pl-lang") > first match in
   navigator.languages (ko-KR -> ko, zh-TW -> zh-Hant, pt-PT -> pt-BR) > stay on the English root.
   Redirect only when the language is not English and A has it; otherwise the page stays (no fallback to the next browser language).
   ?lang=xx (company-wide hand-off): a supported language is saved and the page moves to "/xx/<same path>"
   (en stays on the page, the query is cleaned); an unsupported one is ignored and the later steps decide. Other query params and #hash are kept.
   No server redirect: crawlers see "/" as English. */
(function(){
  var S=/*SUPPORTED*/[],A=/*AVAILABLE*/[];
  /* "ko-KR" -> "ko", "zh_TW" -> "zh" ... first supported match for a language tag, or '' */
  function pick(c){
    c=String(c||'').toLowerCase().replace(/_/g,'-');
    /* legacy codes: Android/old browsers say "in" for Indonesian. Chinese: only Traditional (zh-TW/HK/MO/Hant) is a site language; Simplified is not. */
    var b=c.split('-')[0];
    if(b==='in')b='id';
    if(b==='zh'){var r=c.split('-').slice(1);var hant=r.indexOf('hant')>=0||(r.indexOf('hans')<0&&(r.indexOf('tw')>=0||r.indexOf('hk')>=0||r.indexOf('mo')>=0));return hant&&S.indexOf('zh-Hant')>=0?'zh-Hant':''}
    if(b==='pt')return S.indexOf('pt-BR')>=0?'pt-BR':'';
    return S.indexOf(b)>=0?b:'';
  }
  try{
    var seg=location.pathname.split('/')[1];
    if(seg&&(S.indexOf(seg)>=0||seg==='pt'||seg==='zh'||seg==='ru'))return;
    var to='',saved='',q=location.search||'',keep='',hasLang=false;
    var parts=q.replace(/^\?/,'').split('&').filter(Boolean),rest=[],want='';
    for(var j=0;j<parts.length;j++){
      var kv=parts[j].split('=');
      if(kv[0]==='lang'){hasLang=true;if(!want){try{want=pick(decodeURIComponent((kv.slice(1).join('=')||'').replace(/\+/g,' ')))}catch(e){}}}
      else rest.push(parts[j]);
    }
    keep=rest.length?'?'+rest.join('&'):'';
    if(want){
      try{localStorage.setItem('pl-lang',want)}catch(e){}
      if(want==='en'){
        if(hasLang&&history.replaceState)history.replaceState(null,'',location.pathname+keep+location.hash);
        return;
      }
      to=want;
    }else{
      try{saved=localStorage.getItem('pl-lang')||''}catch(e){}
      if(S.indexOf(saved)>=0)to=saved;
      else{
        var L=(navigator.languages&&navigator.languages.length)?navigator.languages:[navigator.language||''];
        for(var i=0;i<L.length&&!to;i++)to=pick(L[i]);
      }
    }
    if(to&&to!=='en'&&A.indexOf(to)>=0)location.replace('/'+to+location.pathname+keep+location.hash);
    else if(want&&history.replaceState)history.replaceState(null,'',location.pathname+keep+location.hash);
  }catch(e){}
})();

