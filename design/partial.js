  /* ================ THE DESIGN SYSTEM, ONE SOURCE: BEHAVIOUR ================
     Inlined into every template by tools/build-templates.py, after `var DICT`.
     Every page builds its whole DOM from the JSON in <script id="data"> with the
     helpers below. Strings reach the DOM through textContent only. */

  /* ---------- the dictionary ---------- */
  var LANG='en';
  function L(k){
    var d=DICT[LANG]||DICT.en, v=d[k];
    if(v==null) v=DICT.en[k];
    return v==null ? k : v;
  }
  /* fill {name} slots. Values are inserted as text, never parsed. */
  function F(s,vars){
    return String(s).replace(/\{(\w+)\}/g,function(m,k){ return vars && vars[k]!=null ? String(vars[k]) : m; });
  }
  /* a plural entry is a pair, singular first. Numerals stay numerals. */
  function P(k,n,vars){
    var v=L(k); if(Object.prototype.toString.call(v)==='[object Array]') v = n===1 ? v[0] : v[1];
    var o={n:n}; if(vars) for(var x in vars) o[x]=vars[x];
    return F(v,o);
  }

  /* ---------- DOM ---------- */
  function $(id){ return document.getElementById(id); }
  function el(tag,cls,text){
    var n=document.createElement(tag);
    if(cls) n.className=cls;
    if(text!=null) n.textContent=text;
    return n;
  }
  function add(parent){
    for(var i=1;i<arguments.length;i++){
      var c=arguments[i];
      if(c==null) continue;
      parent.appendChild(typeof c==='string' ? document.createTextNode(c) : c);
    }
    return parent;
  }
  var SVGNS='http://www.w3.org/2000/svg';
  function glyph(id,cls,viewBox){
    var s=document.createElementNS(SVGNS,'svg'), u=document.createElementNS(SVGNS,'use');
    if(cls) s.setAttribute('class',cls);
    if(viewBox) s.setAttribute('viewBox',viewBox);
    u.setAttribute('href','#'+id);
    s.appendChild(u);
    return s;
  }
  /* the channel mark for a source or a message: mail, slack, teams */
  function channel(c,cls){
    var id = c==='slack' ? 'i-slack' : c==='teams' ? 'i-teams' : 'i-mail';
    return glyph(id, cls||'ch');
  }
  /* an href is set only after a check. Anything else is a dead link that does nothing. */
  function safeHref(a,href){
    var h=(href==null?'':String(href)).trim();
    if(/^(https:\/\/|mailto:|#)/.test(h) && h!=='#'){ a.setAttribute('href',h); return true; }
    a.setAttribute('href','#');
    a.onclick=function(e){ e.preventDefault(); };
    return false;
  }
  function link(href,text,cls){
    var a=el('a',cls,text); safeHref(a,href); return a;
  }
  /* an outside link opens in its own tab, so the page stays where the exec left it */
  function outLink(href,text,cls){
    var a=link(href,text,cls);
    if(a.getAttribute('href')!=='#'){ a.setAttribute('target','_blank'); a.setAttribute('rel','noopener'); }
    return a;
  }

  /* ---------- dates ---------- */
  function isoToday(){
    var d=new Date(), p=function(n){ return (n<10?'0':'')+n; };
    return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate());
  }
  /* true when `iso` is within the last `days` days of `today`, both ISO YYYY-MM-DD */
  function withinDays(iso,today,days){
    if(!iso || !today) return false;
    var a=Date.parse(iso+'T00:00:00Z'), b=Date.parse(today+'T00:00:00Z');
    if(isNaN(a)||isNaN(b)) return false;
    var diff=(b-a)/86400000;
    return diff>=0 && diff<days;
  }
  function minutes(hhmm){
    var m=/^(\d{1,2}):(\d{2})$/.exec(hhmm||''); if(!m) return NaN;
    return parseInt(m[1],10)*60+parseInt(m[2],10);
  }
  /* "30 min", "1 h", "1 h 30": the same shape in both languages */
  function span(mins){
    var h=Math.floor(mins/60), m=mins%60;
    if(h===0) return m+' min';
    return m ? h+' h '+(m<10?'0':'')+m : h+' h';
  }

  /* ---------- shared pieces ---------- */
  var DATA=null, LINKS={}, PAGE_KEY='';
  function loadData(){
    var d=null;
    try{ d=JSON.parse($('data').textContent); }catch(e){ d=null; }
    if(!d || typeof d!=='object'){
      try{ d=JSON.parse($('example').textContent); }catch(e2){ d={}; }
    }
    DATA=d; LANG=(d.lang==='fr')?'fr':'en'; LINKS=d.links||{};
    document.documentElement.setAttribute('lang',LANG);
    return d;
  }
  /* the header: the notebook page, the date and the time in the hand, the count, the sub */
  function header(page,pageKey,h1){
    PAGE_KEY=pageKey;
    add(page, el('div','book',L(pageKey)));
    var top=el('div','top');
    add(top, el('span','eyebrow',DATA.date_label||''), el('span','eyebrow',DATA.time_label||''));
    add(page, top, el('h1',null,h1), el('p','sub',DATA.sub||''));
    document.title=L(pageKey);
  }
  /* a section head: label, rule, tally. `extra` is an optional element at the end. */
  function h2(label,tally,extra){
    var h=el('h2'); add(h, label, el('i'));
    if(tally!=null){ var b=el('b'); if(typeof tally==='string') b.textContent=tally; else add(b,tally); add(h,b); }
    if(extra) add(h,extra);
    return h;
  }
  function cap(lines){
    var c=el('div','cap'); (lines||[]).forEach(function(s){ add(c, el('span',null,s)); }); return c;
  }
  /* the sources row: three at most, then the gesture at the right end */
  function srcRow(sources,briefing,gestureLabel,extra){
    var d=el('div','src'), list=(sources||[]).slice(0,3);
    list.forEach(function(s){
      var a=link(s.href,''); a.textContent='';
      add(a, el('i',null, s.via || L('k_'+(s.kind||'doc'))), s.label||'');
      if(a.getAttribute('href')!=='#'){ a.setAttribute('target','_blank'); a.setAttribute('rel','noopener'); }
      add(d,a);
    });
    if(extra) add(d,extra);
    if(briefing){
      var a2=el('a','ask',gestureLabel||L('ask'));
      if(DATA.gesture==='link'){
        safeHref(a2,'https://claude.ai/new?q='+encodeURIComponent(briefing)+'&surface=cowork&composer=mini');
        a2.setAttribute('target','_blank'); a2.setAttribute('rel','noopener');
      } else {
        a2.setAttribute('href','#');
        a2.dataset.q=encodeURIComponent(briefing);
        a2.onclick=function(e){ return ask(e,a2); };
      }
      add(d,a2);
    }
    return d;
  }
  /* a cross-reference carries its whole substance as link text. Same page: opens the
     target. Another page: a plain link to that page's artefact plus the id. */
  function goRow(g){
    var d=el('div','go'), a;
    if(g.page){
      var base=LINKS[g.page]||'';
      a=link(base ? base+'#'+g.id : '', g.text);
    } else {
      a=el('a',null,g.text); a.setAttribute('href','#'+g.id);
      a.onclick=function(e){ jump(e,g.id); };
    }
    add(d,a);
    return d;
  }
  function goRows(box,list){ (list||[]).forEach(function(g){ add(box,goRow(g)); }); }
  function paras(box,list,cls){
    (list||[]).forEach(function(s){ if(s) add(box, el('p',cls,s)); });
  }
  /* the type, as a tag: precedent, knock_on, pattern, history, rule */
  function typeTag(type){ return el('span','tag',L('t_'+type)); }
  function footer(spans){
    var f=el('footer'); (spans||[]).forEach(function(s){ add(f, el('span',null,s||'')); }); return f;
  }
  function credit(){
    var p=el('p','by');
    add(p, L('by')+' ', outLink('https://www.linkedin.com/in/paul-rousselle/', L('by_name')), ' '+L('by_tail')+' ',
        glyph('i-mark','mark','3 17 90 58'));
    return p;
  }
  /* a quiet mark on a row, in pine, for a moment: "Saved". Or in brick: "Not saved". */
  function flash(row,text,bad){
    var dec=row.querySelector('.dec')||row.querySelector('button');
    var old=row.querySelector('.rel.tmp'); if(old) old.parentNode.removeChild(old);
    var s=el('span','rel tmp '+(bad?'cf':'nw'),text);
    add(dec,s);
    setTimeout(function(){ if(s.parentNode) s.parentNode.removeChild(s); },2000);
  }

  /* ---------- the database, when this view can run it ----------
     `window.claude` carries `use` and nothing else. The namespace arrives through the
     promise, never at first paint, and `null` means this view cannot run it: a plain
     browser, a saved file, a host that never answers. Every page renders without it
     and lights the writes up when it resolves. */
  var DB=null, DB_KNOWN=false, onDb=function(){};
  function dbInit(cb){
    onDb=cb||function(){};
    try{
      if(window.claude && typeof window.claude.use==='function'){
        window.claude.use('db').then(function(d){ DB=d||null; DB_KNOWN=true; onDb(); },
                                     function(){ DB=null; DB_KNOWN=true; onDb(); });
        return;
      }
    }catch(e){}
    DB=null; DB_KNOWN=true; onDb();
  }

  /* ---------- interaction ---------- */
  /* the lists: one row open at a time, so the page never becomes a wall */
  function t(b){
    var r=b.parentNode, was=r.classList.contains('open');
    document.querySelectorAll('.row.open').forEach(function(o){
      o.classList.remove('open');
      var ob=o.querySelector('button'); if(ob) ob.setAttribute('aria-expanded','false');
    });
    if(!was){ r.classList.add('open'); b.setAttribute('aria-expanded','true'); }
  }

  /* the strip: one brief at a time, so the day never grows a second page */
  function m(btn){
    var brief=document.getElementById(btn.dataset.b); if(!brief) return false;
    var wasOpen=brief.classList.contains('on');
    document.querySelectorAll('.mt').forEach(function(b){
      b.classList.remove('on'); b.setAttribute('aria-expanded','false');
    });
    document.querySelectorAll('.mbrief').forEach(function(b){ b.classList.remove('on'); });
    if(!wasOpen){
      brief.classList.add('on');
      btn.classList.add('on');
      btn.setAttribute('aria-expanded','true');
    }
    return !wasOpen;
  }

  /* copying, shared by Ask Claude, Draft the note, Keep, Drop and Copy for Claude.
     execCommand stays as the fallback because it is the one that still works inside a
     sandboxed iframe without allow-same-origin, which is exactly the published-artefact
     case. A silent execCommand failure is a failure: `fail` runs, `done` does not. */
  function copyText(q,done,fail){
    var fb=function(){
      var ta=document.createElement('textarea'), ok=false;
      ta.value=q; ta.style.cssText='position:fixed;top:0;left:0;opacity:0';
      document.body.appendChild(ta); ta.select();
      try{ ok=document.execCommand('copy'); }catch(x){ ok=false; }
      document.body.removeChild(ta);
      if(ok) done(); else fail();
    };
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(q).then(done,fb);
    } else { fb(); }
  }

  /* Ask Claude copies a standalone briefing. A second click while it still says
     Copied does nothing, so the label can never be captured as the confirmation. The
     real label is captured and restored. A blocked copy says so, and the page goes on. */
  function ask(e,a){
    e.preventDefault();
    if(a.classList.contains('ok')) return false;
    var label=a.textContent, say=function(s){
      a.textContent=s; a.classList.add('ok');
      setTimeout(function(){ a.textContent=label; a.classList.remove('ok'); },2600);
    };
    copyText(decodeURIComponent(a.dataset.q||''),
      function(){ say(L('copied')); },
      function(){ say(L('blocked')); });
    return false;
  }

  /* a cross-reference lands on its target already open, so you never arrive at a
     closed line and have to guess which one was meant. A block on the strip opens its
     brief; a flat row has nothing to open. */
  function jump(e,id){
    if(e && e.preventDefault) e.preventDefault();
    var el_=document.getElementById(id); if(!el_) return;
    if(el_.classList.contains('mt')){
      if(!el_.classList.contains('on')) m(el_);
    } else {
      var b=el_.querySelector('button');
      if(b && !el_.classList.contains('flat') && !el_.classList.contains('open')) t(b);
    }
    el_.scrollIntoView({behavior:'smooth',block:'center'});
  }
  /* a row closed from code: the toggle's state follows */
  function closeRow(r){
    r.classList.remove('open');
    var b=r.querySelector('button'); if(b) b.setAttribute('aria-expanded','false');
  }

  /* ---------- drop, with a reason ----------
     The one gesture the exec has on a line they did not write: Drop, then why. The
     word at the end of the sources row becomes the reasons, inline. A choice writes
     dismissals/<slug of ref> when this view can run the store, and otherwise copies
     a one-line briefing and marks the row "waiting for Claude". The row stays where
     it was, greyed: never moved, never hidden. */
  /* the document id: lowercase, anything not a letter or a digit as "-", 80 at most */
  function slug(s){
    return String(s==null?'':s).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,80);
  }
  /* a reason as the word the exec chose, for a marker or a briefing: "done" */
  var REASON_KEY={done:'drop_done', not_important:'drop_unimportant',
                  not_a_priority:'drop_not_priority', not_a_decision:'drop_not_decision'};
  function reasonWord(reason){
    var w=L(REASON_KEY[reason]||reason); return w.charAt(0).toLowerCase()+w.slice(1);
  }
  /* the reasons in place of the gesture that asked. `anchor` and `hideAlso` hide
     while the question is up; Cancel brings them back. `pick(reason, q, restore)`
     runs on a choice with the question still up, so a failure can be said beside
     it, and `restore` is the way out. Returns the question element. */
  function askReason(anchor,choices,pick,hideAlso){
    var next=anchor.nextSibling;
    if(next && next.classList && next.classList.contains('dropq')) return next;
    var q=el('span','dropq'), hid=[anchor].concat(hideAlso||[]);
    var restore=function(){
      hid.forEach(function(x){ x.style.display=''; });
      if(q.parentNode) q.parentNode.removeChild(q);
    };
    hid.forEach(function(x){ x.style.display='none'; });
    choices.forEach(function(c){
      var b=el('button',null,c[1]); b.type='button';
      b.onclick=function(){ pick(c[0],q,restore); };
      add(q,b);
    });
    var x=el('button','x',L('cancel')); x.type='button';
    x.onclick=function(){ restore(); if(anchor.focus) anchor.focus(); };
    add(q, x, el('span','note',''));
    anchor.parentNode.insertBefore(q,anchor.nextSibling);
    q.firstChild.focus();
    return q;
  }
  /* the shared gesture: Drop at the end of the row's sources line, after Ask Claude.
     spec = {page, kind, ref, say}: page is the store's word (brief, inbox, context),
     kind is queue | decision | job | topic, ref the stable key of the line. The
     dictionary lookup can be passed as the third argument; the page's own is used
     otherwise. */
  var DROP_ROWS=[];
  function dropUI(row,spec,L_){
    var T=L_||L, src=row.querySelector('.src'); if(!src) return null;
    var a=el('a','drop',T('drop_line')); a.setAttribute('href','#');
    a.onclick=function(e){
      e.preventDefault();
      askReason(a, [['done',T('drop_done')],['not_important',T('drop_unimportant')]],
        function(reason,q,restore){ dismiss(row,spec,reason,q,restore); });
      return false;
    };
    add(src,a);
    DROP_ROWS.push({row:row, spec:spec});
    return a;
  }
  /* the state a remembered drop leaves on its row: closed, greyed, the Drop word
     gone, the marker. The same whether the drop was made now or read back from the
     store. A row already gone is left as it is, so applying it twice is harmless. */
  function dropped(row,reason){
    if(row.classList.contains('gone')) return false;
    var a=row.querySelector('.src .drop'); if(a) a.parentNode.removeChild(a);
    closeRow(row);
    row.classList.add('gone');
    var dec=row.querySelector('.dec');
    if(dec) add(dec, el('span','rel nw',L(reason==='done' ? 'dropped_done_m' : 'dropped_unimportant_m')));
    return true;
  }
  /* the write, or the briefing. With the store: one document, the row closes and
     says "remembered". Without it: the briefing is copied, the row stays open on
     "Copied" so the exec knows to paste, and says "waiting for Claude". A failed
     write or a blocked copy says so and leaves the line as it was. */
  function dismiss(row,spec,reason,q,restore){
    var btns=Array.prototype.slice.call(q.querySelectorAll('button')), note=q.querySelector('.note');
    var lock=function(on){ btns.forEach(function(b){ b.disabled=on; }); };
    var setNote=function(s,bad){ note.textContent=s; note.className='note'+(bad?' bad':''); };
    var mark=function(text){
      row.classList.add('gone');
      var dec=row.querySelector('.dec'); if(dec) add(dec, el('span','rel nw',text));
    };
    lock(true); setNote('');
    if(DB){
      var id=slug(spec.ref)||slug(row.id)||'line';
      var body={page:spec.page, kind:spec.kind, ref:String(spec.ref==null?'':spec.ref),
                say:spec.say||'', reason:reason, date:DATA.today||isoToday()};
      DB.doc('dismissals/'+id).set(body).then(function(){
        restore(); dropped(row,reason);
      }, function(err){
        lock(false); setNote(L('not_saved')+(err && err.message ? ' · '+err.message : ''), true);
      });
    } else {
      /* the sentence loses its full stop inside the quotes, so the line has one stop */
      var text=F(L('drop_briefing'),{page:L(PAGE_KEY||('page_'+spec.page)), say:String(spec.say||'').replace(/[.\s]+$/,''), reason:reasonWord(reason)});
      copyText(text, function(){
        setNote(L('copied'));
        mark(L('dropped_m')+', '+reasonWord(reason)+', '+L('waiting'));
      }, function(){ lock(false); setNote(L('blocked'),true); });
    }
  }

  /* ---------- what the exec did since publish ----------
     A drop writes the store, and nothing republishes the page until the next
     routine run. So once the store resolves, the page reads `dismissals` and applies
     each document to the row it names, page and ref both matching the spec dropUI
     registered: the same state a fresh drop leaves, without the write. The rows are
     listened to, so a drop made in another open tab lands here too; where the store
     cannot subscribe, one read. A document this tab is still writing is skipped, so
     the write's own confirmation is the only hand on that row. A read that fails, or
     a store that is null, changes nothing: the page stays as rendered from its JSON
     and no error is shown, since only writes have feedback. `then` runs after every
     delivery so the page can recount what it shows. */
  var DROP_SUB=null;
  function hydrateDrops(then){
    if(!DB || DROP_SUB || !DROP_ROWS.length) return;
    var apply=function(snap){
      (snap && snap.docs || []).forEach(function(ds){
        if(!ds.exists || (ds.metadata && ds.metadata.hasPendingWrites)) return;
        var d=ds.data()||{}, ref=String(d.ref==null?'':d.ref);
        if(!ref) return;
        DROP_ROWS.forEach(function(x){
          if(x.spec.page!==d.page || String(x.spec.ref==null?'':x.spec.ref)!==ref) return;
          dropped(x.row, d.reason==='done' ? 'done' : 'not_important');
        });
      });
      if(then) then();
    };
    var safe=function(snap){ try{ apply(snap); }catch(e){} };
    var col;
    try{ col=DB.collection('dismissals'); }catch(e){ return; }
    var once=function(){ try{ col.get().then(safe, function(){}); }catch(e){} };
    if(typeof col.onSnapshot!=='function'){ once(); return; }
    var got=false;
    try{
      DROP_SUB=col.onSnapshot(function(s){ got=true; safe(s); }, function(){ if(!got) once(); });
    }catch(e){ once(); }
  }
