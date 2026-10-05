  /* ================ THE LIVE KIT ================
     What the Daily brief and Super Context share once they are opened in Claude with
     their capabilities: the connections (mail, calendar, chat), Claude's two panels (a
     summary and a draft), the banner, the page's own store, and the demo's simulated
     world. The inbox keeps its own layer (design/live-inbox.js), tested as it is.

     Every name here starts with lk or LK: the page's script is global. A page's layer
     calls lkKit(BASE) once, with the JSON a run filled, and builds on what it returns.
     Nothing here runs on its own and nothing here writes outside the page's store,
     except a draft the exec asks for. A chat message is copied, never sent. */
function lkKit(BASE){
  'use strict';
  var CFG=BASE.live||{}, DEMO=CFG.demo||null;
  var K={DEMO:DEMO, CFG:CFG, db:null, mcp:null, sample:null, ME:CFG.me||{}};
  var LANG_NAME=K.LANG_NAME={en:'English', fr:'French'}[LANG]||'English';
  var T0=Date.now();

  /* ---------- helpers ---------- */
  function T(k,v){ return v ? F(L(k),v) : L(k); }
  function plainText(s){ try{ return new DOMParser().parseFromString(String(s||''),'text/html').documentElement.textContent||''; }catch(e){ return String(s||''); } }
  function cut(s,n){ s=String(s||'').replace(/[͏‌­\s]+/g,' ').trim(); return s.length>n ? s.slice(0,n-1)+'…' : s; }
  function addrOf(s){ var m=String(s||'').match(/<([^>]+)>/); return (m?m[1]:String(s||'')).trim().toLowerCase(); }
  function nameOf(s){ var x=String(s||''), m=x.match(/^\s*"?([^"<]+?)"?\s*</); return m?m[1]:x; }
  function pad(n){ return (n<10?'0':'')+n; }
  function hhmm(d){ return pad(d.getHours())+':'+pad(d.getMinutes()); }
  function dayOf(d){ return d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate()); }
  function since(t0){ var s=(performance.now()-t0)/1000; return s.toFixed(0)+' s'; }
  function pause(ms){ return new Promise(function(r){ setTimeout(r,ms); }); }
  function slugOf(s){ return slug(s)||'x'; }
  function quiet(text){ var b=el('button','lxq',text); b.type='button'; return b; }
  /* a button in a sources row: a small outlined pill; main is the one that starts the work */
  function pill(text,main){ var a=el('a','lxa'+(main?' main':''),text); a.setAttribute('href','#'); a.setAttribute('role','button'); a.setAttribute('aria-expanded','false'); return a; }
  /* the clock: the demo runs on its own morning, so it reads the same whenever it is opened */
  function now(){
    if(DEMO&&DEMO.now){ var p=String(DEMO.now).split(':'), d=new Date(); d.setHours(+p[0],+p[1],0,0); return new Date(d.getTime()+(Date.now()-T0)); }
    return new Date();
  }
  function when(d){ if(!d||isNaN(d)) return ''; var mo=L('lx_months'); return dayOf(d)===dayOf(now()) ? hhmm(d) : d.getDate()+' '+mo[d.getMonth()]; }
  function minutesOf(s){ var m=/^(\d{1,2}):(\d{2})$/.exec(String(s||'')); return m ? (+m[1])*60+(+m[2]) : NaN; }
  /* per viewer, this browser only, never shared and never read by a run */
  function keep(k,v){ if(DEMO) return null; try{ if(v===undefined) return JSON.parse(window.localStorage.getItem(k)||'null'); window.localStorage.setItem(k,JSON.stringify(v)); }catch(e){ return null; } }
  Object.assign(K,{T:T, plainText:plainText, cut:cut, addrOf:addrOf, nameOf:nameOf, hhmm:hhmm, dayOf:dayOf, since:since,
    pause:pause, slugOf:slugOf, quiet:quiet, pill:pill, now:now, when:when, minutesOf:minutesOf, keep:keep});

  /* the exec, as Claude should write for them: first name, role, and the language */
  K.who=function(){ var m=K.ME; return (m.name||L('you'))+(m.role?', '+m.role:''); };
  K.firstName=function(){ return String(K.ME.name||'').split(/\s+/)[0]||''; };

  /* ---------- the mail connection: one adapter per connector the run named ---------- */
  var ACCT={};
  function threadUrl(email,id){ if(DEMO) return ''; try{ return 'https://mail.google.com/mail/?authuser='+encodeURIComponent(email)+'#all/thread-f:'+BigInt('0x'+id).toString(); }catch(e){ return 'https://mail.google.com/mail/?authuser='+encodeURIComponent(email); } }
  var MAIL_ADAPTERS={
    /* Aureol Connect: several Google accounts, threads by id per account */
    aureol:{
      tools:['gmail_search','gmail_get_thread','gmail_create_draft','gmail_update_draft'],
      call:function(q,n){ return ['gmail_search',{account:'all',query:q,page_size:n||20}]; },
      parse:function(p){
        return ((p||{}).threads||[]).map(function(t){
          var a=t.account||{}, email=String(a.email||'').toLowerCase(), alias=a.alias||email; ACCT[alias]=email;
          var from=addrOf(t.from);
          return {id:'m:'+t.thread_id, thread:t.thread_id, account:alias, from:plainText(nameOf(t.from)), fromAddr:from,
            mine:!!email&&from===email, subject:plainText(t.subject||L('lx_no_subject')), snippet:cut(plainText(t.snippet),240),
            date:new Date(t.date), href:threadUrl(email,t.thread_id), unread:t.unread!==false, count:t.message_count||1};
        });
      },
      thread:async function(x){
        var r=await K.mcp.callTool(K.MAIL_CFG.server,'gmail_get_thread',{account:x.account,thread_id:x.thread,format:'text',max_chars:30000});
        return (((r||{}).payload||{}).messages||[]).map(function(m){
          return {from:plainText(nameOf(m.from||'')), fromAddr:addrOf(m.from), date:m.date, subject:plainText(m.subject||''), body:String(m.body||'')}; });
      },
      /* a reply inside its thread, or a new mail; the same token updates the draft it made */
      draft:async function(g,body,token){
        var srv=K.MAIL_CFG.server, d;
        if(token) d=(await K.mcp.callTool(srv,'gmail_update_draft',{account:g.account,draft_token:token,body:body})).payload||{};
        else if(g.thread) d=(await K.mcp.callTool(srv,'gmail_create_draft',{account:g.account,body:body,reply_to_thread_id:g.thread,reply_all:!!g.all})).payload||{};
        else d=(await K.mcp.callTool(srv,'gmail_create_draft',{account:g.account,body:body,to:g.to||[],subject:g.subject||''})).payload||{};
        return {token:d.draft_token||token||null, url:d.gmail_url, to:(d.to||g.to||[]).concat(d.cc||[]), outside:d.recipients_outside_thread||[]};
      }
    },
    /* the Gmail connector: one account */
    gmail:{
      tools:['search_threads','get_thread','create_draft','update_draft'],
      call:function(q,n){ return ['search_threads',{query:q,pageSize:n||20,view:'THREAD_VIEW_MINIMAL'}]; },
      parse:function(p){
        return ((p||{}).threads||[]).map(function(t){
          var ms=(t.messages||[]).slice().sort(function(a,b){ return new Date(a.date)-new Date(b.date); }), m=ms[ms.length-1]||{};
          return {id:'m:'+t.id, thread:t.id, account:'gmail', lastId:m.id, from:plainText(nameOf(m.sender||'')), fromAddr:addrOf(m.sender),
            mine:(m.labelIds||[]).indexOf('SENT')>=0, subject:plainText(m.subject||L('lx_no_subject')), snippet:cut(plainText(m.snippet),240),
            date:new Date(m.date), href:t.viewUrl||'', unread:ms.some(function(x){ return (x.labelIds||[]).indexOf('UNREAD')>=0; }), count:t.messageCount||ms.length};
        });
      },
      thread:async function(x){
        var r=await K.mcp.callTool(K.MAIL_CFG.server,'get_thread',{threadId:x.thread,messageFormat:'PLAIN_TEXT'});
        return (((r||{}).payload||{}).messages||[]).map(function(m){
          return {id:m.id, from:plainText(nameOf(m.sender||'')), fromAddr:addrOf(m.sender), date:m.date, subject:plainText(m.subject||''),
            body:String(m.plaintextBody||m.snippet||''), mine:(m.labelIds||[]).indexOf('SENT')>=0}; });
      },
      draft:async function(g,body,token){
        var srv=K.MAIL_CFG.server;
        if(token){ var u=(await K.mcp.callTool(srv,'update_draft',{draftId:token,body:body})).payload||{}; return {token:u.id||token, url:u.viewUrl, to:[], outside:[]}; }
        var input={body:body};
        if(g.thread){
          var ms=await MAIL_ADAPTERS.gmail.thread(g), last=null;
          for(var i=ms.length-1;i>=0;i--){ if(!ms[i].mine){ last=ms[i]; break; } }
          last=last||ms[ms.length-1]||{};
          var subj=String(last.subject||''); if(!/^re\s*:/i.test(subj)) subj='Re: '+subj;
          input.subject=subj; if(last.id) input.replyToMessageId=last.id; if(last.fromAddr&&!last.mine) input.to=[last.fromAddr];
        } else { input.to=g.to||[]; input.subject=g.subject||''; }
        var d=(await K.mcp.callTool(srv,'create_draft',input)).payload||{};
        return {token:d.id||null, url:d.viewUrl, to:input.to||[], outside:[]};
      }
    }
  };
  Object.keys(MAIL_ADAPTERS).forEach(function(k){ var a=MAIL_ADAPTERS[k];
    a.search=async function(q,n){ var c=a.call(q,n), r=await K.mcp.callTool(K.MAIL_CFG.server,c[0],c[1]); return a.parse((r||{}).payload); }; });
  K.MAIL_CFG=CFG.mail||null;
  K.MAIL=K.MAIL_CFG&&MAIL_ADAPTERS[K.MAIL_CFG.api] ? MAIL_ADAPTERS[K.MAIL_CFG.api] : null;
  K.MAIL_NAME=DEMO&&DEMO.mail_name ? DEMO.mail_name : 'Gmail';
  /* the threads the exec wrote in since a time; a run's time in Gmail's own syntax */
  function epoch(iso){ return Math.floor(Date.parse(iso)/1000); }
  K.sentQuery=function(iso,to){ return 'in:sent'+(to?' to:'+to:'')+' after:'+epoch(iso); };
  K.threadText=async function(g,last,chars){
    var ms=await K.MAIL.thread(g);
    return ms.slice(-(last||8)).map(function(m){ return 'From: '+m.from+(m.fromAddr?' <'+m.fromAddr+'>':'')+'\nDate: '+m.date+'\nSubject: '+m.subject+'\n\n'+String(m.body||'').slice(0,chars||3000); }).join('\n\n---\n\n');
  };

  /* ---------- the calendar: today's events, one adapter per connector ---------- */
  var CAL_ADAPTERS={
    aureol:{
      tools:['calendar_list_events'],
      call:function(){ var d=now(); return ['calendar_list_events',{account:'all',time_min:dayOf(d),time_max:dayOf(new Date(d.getTime()+864e5)),page_size:100}]; },
      parse:function(p){
        var seen={};
        return ((p||{}).events||[]).filter(function(e){
          var k=e.ical_uid||e.event_id; if(seen[k]) return false; seen[k]=1; return true;
        }).map(function(e){
          return {id:e.event_id, title:plainText(e.summary||''), start:new Date(e.start), end:new Date(e.end), allDay:!!e.all_day,
            busy:e.busy!==false, declined:e.my_response==='declined', cancelled:e.status==='cancelled', href:e.html_link||'',
            organizer:String(e.organizer||'').toLowerCase(), account:(e.account||{}).alias||''};
        });
      }
    },
    /* the Google Calendar connector: the primary calendar */
    gcal:{
      tools:['list_events'],
      call:function(){ var a=new Date(now()); a.setHours(0,0,0,0); var b=new Date(a.getTime()+864e5);
        return ['list_events',{startTime:a.toISOString(),endTime:b.toISOString(),orderBy:'startTime',pageSize:100}]; },
      parse:function(p){
        return ((p||{}).events||[]).map(function(e){
          var s=(e.start||{}), f=(e.end||{}), me=(e.attendees||[]).filter(function(x){ return x.self; })[0];
          return {id:e.id, title:plainText(e.summary||''), start:new Date(s.dateTime||s.date), end:new Date(f.dateTime||f.date), allDay:!s.dateTime,
            busy:e.transparency!=='transparent', declined:!!(me&&me.responseStatus==='declined'), cancelled:e.status==='cancelled',
            href:e.htmlLink||'', organizer:String((e.organizer||{}).email||'').toLowerCase(), account:''};
        });
      }
    }
  };
  K.CAL_CFG=CFG.calendar||null;
  K.CAL=K.CAL_CFG&&CAL_ADAPTERS[K.CAL_CFG.api] ? CAL_ADAPTERS[K.CAL_CFG.api] : null;

  /* ---------- chat: Slack, read and copied, never sent ---------- */
  K.CHAT_CFG=CFG.chat&&CFG.chat.api==='slack' ? CFG.chat : null;
  K.CHAT_NAME=K.CHAT_CFG ? K.CHAT_CFG.server : L('f_chat');
  K.slackText=async function(ch){
    var r=await K.mcp.callTool(K.CHAT_CFG.server,'slack_read_channel',{channel_id:ch,limit:20,response_format:'concise'});
    var p=(r||{}).payload; return typeof p==='string' ? p : String((p&&p.messages)||'');
  };

  /* the DMs the exec wrote in after a time, from Slack's search: {channel id: true}. The exec is the one
     person in every conversation the search returns, or the one alone in a conversation with themselves */
  K.slackCall=function(sinceIso){ var d=new Date(Date.parse(sinceIso)-864e5);
    return ['slack_search_public_and_private',{filters:'is:dm after:'+dayOf(d),limit:20,sort:'timestamp',include_context:false,natural_language_query:''}]; };
  K.slackMine=function(p,sinceIso){
    var md=String((p&&typeof p==='object')?p.results:p||''), all=[], me=null, out={}, since=Date.parse(sinceIso)/1000;
    md.split(/\n### Result /).slice(1).forEach(function(b){
      var g=function(re){ var m=b.match(re); return m?m[1].trim():''; };
      all.push({ch:g(/Channel:[^\n]*\(ID: ([A-Z0-9]+)\)/), from:g(/From:[^\n]*\(ID: ([A-Z0-9]+)\)/), ts:parseFloat(g(/Message_ts: ([0-9.]+)/))||0,
        parts:(g(/Participants: ([^\n]+)/).match(/ID: [A-Z0-9]+/g)||[]).map(function(x){ return x.slice(4); })});
    });
    all.forEach(function(m){ var u=Array.from(new Set(m.parts)); if(u.length===1) me=me||u[0]; });
    if(!me&&all.length>1){ var c={}; all.forEach(function(m){ (new Set(m.parts)).forEach(function(id){ c[id]=(c[id]||0)+1; }); });
      Object.keys(c).forEach(function(id){ if(c[id]===all.length) me=me||id; }); }
    if(DEMO&&DEMO.me_id) me=DEMO.me_id;
    all.forEach(function(m){ if(me&&m.from===me&&m.ts>since&&m.ch) out[m.ch]=true; });
    return out;
  };

  /* ---------- what to say when something could not be done ---------- */
  K.mcpCopy=function(e,server){ var c=e&&e.code;
    if(c==='needs_reauth') return T('lx_e_reauth',{s:server});
    if(c==='server_not_connected') return T('lx_e_add',{s:server});
    if(c==='not_in_manifest'||c==='not_granted') return T('lx_e_grant',{s:server});
    return T('lx_e_read',{s:server, c:c||'error'}); };
  K.sampleCopy=function(e){ var c=e&&e.code;
    if(c==='not_granted'||c==='sampling_disabled') return L('lx_s_grant');
    if(c==='rate_limited') return L('lx_s_rate');
    if(c==='invalid_json') return L('lx_s_json');
    return T('lx_s_stop',{c:c||cut(String((e&&e.message)||e||'error'),140)}); };

  /* ---------- the banner: one quiet line that runs while the page reads ---------- */
  K.banner=function(text){
    var r=el('div','lxrun'), t=el('span',null,text), bar=el('span','lxbar'), s=el('span','lxsecs',''), t0=performance.now(), iv=null;
    r.setAttribute('role','status'); r.setAttribute('aria-live','polite');
    bar.appendChild(el('i')); add(r,t,bar,s);
    r.run=function(x){ r.classList.remove('done','bad'); if(x!=null) t.textContent=x; t0=performance.now(); s.textContent=''; clearInterval(iv); iv=setInterval(function(){ s.textContent=since(t0); },500); };
    r.done=function(x){ clearInterval(iv); r.classList.add('done'); r.classList.remove('bad'); if(x!=null) t.textContent=x; s.textContent=''; };
    r.fail=function(x){ clearInterval(iv); r.classList.add('done','bad'); t.textContent=x; s.textContent=''; };
    r.text=t; r.run(text);
    return r;
  };
  K.skeleton=function(n){
    var f=el('div','lkskel');
    for(var i=0;i<n;i++){ var sk=el('div','lxskel'); add(sk,el('i'),el('i')); f.appendChild(sk); }
    return f;
  };
  /* the typed rows a summary is drawn in: the design system's tags */
  K.ctxRows=function(rows){
    var c=el('div','ctx');
    rows.forEach(function(r){
      if(!r||!r.items||!r.items.length) return;
      add(c, el('span','tag',r.tag));
      if(r.list){ var ol=el('ol','with'); r.items.forEach(function(w){ var li=el('li'); add(li, el('b',null,w.head||''), el('span',null,String(w.text||''))); add(ol,li); }); add(c,ol); }
      else { var d=el('div'); r.items.forEach(function(x){ add(d, el('p',r.cls||null,String(x))); }); add(c,d); }
    });
    return c;
  };

  /* ---------- a summary, from Claude, kept in the page's store until its sources move ----------
     o: {doc: store path or null, key: what the sources are now, gather: async () => text or '',
         ask: the instructions, show: (answer, body) draws it, empty: what to say when there is nothing,
         canned: a demo's answer} */
  K.summaryPanel=function(o){
    var b=el('div','lxp'), st=el('div','lxline'), meter=el('span','lxmeter',''), body=el('div','lxsum'), note=el('div','lxnote','');
    var foot=el('div','lxline'), redo=quiet(L('lx_redo_sum'));
    add(st,meter); add(foot,redo); if(o.extra) add(foot,o.extra); add(b,st,body,note,foot);
    var busy=false, doc=null; try{ doc=(K.db&&o.doc) ? K.db.doc(o.doc) : null; }catch(e){ doc=null; }
    async function load(force){
      if(busy) return; busy=true; note.textContent=''; note.className='lxnote'; redo.disabled=true;
      var t0=performance.now(), word='', tick=setInterval(function(){ if(word) meter.textContent=word+' '+since(t0); },500);
      try{
        var key=typeof o.key==='function' ? o.key() : o.key;
        if(!force&&doc){ try{ var got=await doc.get(); if(got.exists){ var d=got.data()||{}; if(d.key===key&&d.summary){ body.textContent=''; o.show(d.summary,body); return; } } }catch(e){} }
        if(DEMO&&o.canned&&!K.sample){ word=L('lx_reading'); meter.textContent=word; await pause(900); word=L('lx_summing'); await pause(1100); body.textContent=''; o.show(o.canned,body); return; }
        if(!K.sample){ note.textContent=L('lx_no_claude_here'); note.className='lxnote bad'; return; }
        word=L('lx_reading'); meter.textContent=word;
        var text; try{ text=await o.gather(); }catch(e){ note.textContent=K.mcpCopy(e,o.server||''); note.className='lxnote bad'; return; }
        if(!text){ body.textContent=''; note.textContent=o.empty||''; return; }
        word=L('lx_summing');
        var s=await K.sample.json(o.ask+'\n\n'+text,{modelTier:o.tier||'quick',cache:false});
        s=s&&typeof s==='object'?s:{}; body.textContent=''; o.show(s,body);
        if(doc){ try{ await doc.set({key:key, at:new Date().toISOString(), summary:s}); }catch(e){} }
      }catch(e){ note.textContent=K.sampleCopy(e); note.className='lxnote bad'; }
      finally{ clearInterval(tick); meter.textContent=''; busy=false; redo.disabled=false; }
    }
    redo.onclick=function(){ load(true); };
    b.lxStart=function(){ load(false); };
    return b;
  };

  /* ---------- a draft, from Claude, put in the exec's drafts or copied ----------
     o: {target: {thread, account, all} | {to, subject, account} | {chat: channel id} | null (copy only),
         context: async () => what Claude reads, ask: the instructions, canned: a demo's draft,
         label: the button that saves it, href: where the thread opens} */
  K.draftPanel=function(o){
    var g=o.target||null, mail=!!(g&&!g.chat&&K.MAIL&&(g.thread||(g.to&&g.to.length))&&g.account), chat=!!(g&&g.chat);
    var b=el('div','lxp'), head=el('div','lxline'), wait=el('span','lxmeter',''); add(head,wait);
    var ta=el('textarea','lxta'); ta.hidden=true; ta.setAttribute('aria-label',L('lx_draft_aria'));
    var tweak=el('div','lxline'); tweak.hidden=true; add(tweak, el('span',null,L('lx_change')));
    var tws=[]; [['lx_shorter','Make it shorter.'],['lx_warmer','Make it warmer.'],['lx_formal','Make it more formal.'],['lx_in_en','Rewrite it in English.'],['lx_in_fr','Rewrite it in French.']]
      .forEach(function(c){ var x=quiet(L(c[0])); x.onclick=function(){ revise(c[1]); }; tws.push(x); add(tweak,x); });
    var inp=el('input','lxin'); inp.placeholder=L('lx_change_ph'); inp.setAttribute('aria-label',L('lx_change_ph')); add(tweak,inp);
    var acts=el('div','lxline'); acts.hidden=true;
    var put=el('button','lxgo', mail ? (o.label||L('lx_put')) : L('lx_copy_reply')); put.type='button';
    var to=el('span',null,''), copy=quiet(L('lx_copy')), redo=quiet(L('lx_redo')), stop=quiet(L('lx_stop')); stop.hidden=true;
    var meter=el('span','lxmeter','');
    add(acts,put,to); if(mail) add(acts,copy); add(acts,redo,stop,meter);
    var out=el('div','lxline'), note=el('div','lxnote','');
    add(b,head,ta,tweak,acts,note,out);
    var turns=null, ctl=null, busy=false, token=null;
    function lock(on){ busy=on; [put,redo,copy].concat(tws).forEach(function(x){ x.disabled=on; }); inp.disabled=on; stop.hidden=!on; }
    function bad(s){ note.textContent=s; note.className='lxnote bad'; }
    async function typeOut(text,m){
      lock(true); m.textContent=L('lx_drafting'); await pause(900); ta.hidden=false;
      var words=String(text).split(/(\s+)/), acc='';
      for(var i=0;i<words.length;i++){ acc+=words[i]; ta.value=acc; if(i%6===0) await pause(40); }
      m.textContent=''; lock(false); return text;
    }
    async function run(input,tier,m){
      if(!K.sample&&DEMO&&tier==='default'&&o.canned) return typeOut(o.canned,m);
      if(!K.sample){ bad(L('lx_no_claude_here')); return null; }
      ctl=new AbortController(); lock(true); note.textContent=''; note.className='lxnote';
      var t0=performance.now(), first=null; m.textContent=L('lx_drafting');
      var tick=setInterval(function(){ if(first==null) m.textContent=L('lx_drafting')+' '+since(t0); },500);
      try{
        var r=await K.sample(input,{modelTier:tier,cache:false,signal:ctl.signal,onText:function(u){ if(first==null) first=performance.now(); ta.hidden=false; ta.value=u.text; }});
        m.textContent=''; return r.text;
      }catch(e){ if(e&&e.text) ta.value=e.text; m.textContent=''; if(e&&e.code!=='cancelled') bad(K.sampleCopy(e)); return null; }
      finally{ clearInterval(tick); lock(false); }
    }
    async function draft(){
      if(busy) return; note.textContent=''; out.textContent='';
      var m=acts.hidden?wait:meter; m.textContent=L('lx_reading');
      var ctx=''; try{ ctx=o.context ? await o.context() : ''; }catch(e){ m.textContent=''; bad(K.mcpCopy(e,(K.MAIL_CFG||{}).server||'')); return; }
      turns=[{role:'user', content:o.ask+(ctx?'\n\n'+ctx:'')}];
      var text=await run(turns,'default',m); if(!text) return;
      turns.push({role:'assistant', content:text});
      ta.hidden=false; tweak.hidden=false; acts.hidden=false;
      var who=(g&&g.to&&g.to.length) ? g.to.join(', ') : (o.toName||'');
      to.textContent=(!token&&who)?T('lx_to',{x:who}):'';
    }
    async function revise(change){
      if(busy||!turns) return; var cur=ta.value.trim(); if(!cur) return;
      var t2=turns.slice(0,1).concat([{role:'assistant',content:cur},{role:'user',content:change+' Keep everything else. Reply with the full new version only.'}]);
      var text=await run(t2,'quick',meter); if(text){ turns=t2.concat([{role:'assistant',content:text}]); inp.value=''; }
    }
    function copyIt(done){ var v=ta.value; if(!v) return;
      copyText(v, function(){ note.className='lxnote'; note.textContent=done; if(o.onDone) o.onDone('copied'); }, function(){ ta.select(); note.className='lxnote'; note.textContent=L('lx_copy_blocked'); }); }
    inp.addEventListener('keydown',function(e){ if(e.key==='Enter'){ e.preventDefault(); var v=inp.value.trim(); if(v) revise(v); } });
    stop.onclick=function(){ if(ctl) ctl.abort(); };
    redo.onclick=function(){ draft(); };
    copy.onclick=function(){ copyIt(L('lx_copied')); };
    put.onclick=async function(){
      var text=ta.value.trim(); if(!text||busy) return;
      if(!mail){
        copyIt(chat ? T('lx_copied_chat',{s:K.CHAT_NAME}) : L('lx_copied')); out.textContent='';
        if(o.href) add(out, outLink(o.href,T('lx_open_in',{s:chat?K.CHAT_NAME:K.MAIL_NAME}),'lxout'));
        return;
      }
      lock(true); out.textContent=''; note.className='lxnote'; note.textContent=token?L('lx_updating'):L('lx_saving');
      try{
        var d=null, upd=!!token;
        if(token){ try{ d=await K.MAIL.draft(g,text,token); }catch(e){ if(e&&e.code==='tool_error'){ token=null; upd=false; } else throw e; } }
        if(!d) d=await K.MAIL.draft(g,text,null);
        token=d.token;
        var said=(upd?L('lx_updated'):L('lx_saved'))+(d.to.length?', '+T('lx_to',{x:d.to.join(', ')}):'')+'. '+L('lx_nothing_sent');
        if(d.outside.length) said+=' '+T('lx_outside',{x:d.outside.join(', ')});
        note.textContent=said; put.textContent=L('lx_update'); to.textContent='';
        if(d.url||o.href) add(out, outLink(d.url||o.href,T('lx_open_draft',{s:K.MAIL_NAME}),'lxout'));
        if(o.onDone) o.onDone('saved');
      }catch(e){ bad(e&&e.code==='tool_error' ? T('lx_not_saved',{x:cut(e.message,180)}) : K.mcpCopy(e,K.MAIL_CFG.server)); if(o.href) add(out, outLink(o.href,T('lx_open_in',{s:K.MAIL_NAME}),'lxout')); }
      finally{ lock(false); }
    };
    b.lxStart=function(){ draft(); };
    return b;
  };

  /* ---------- the demo: a store that forgets, and a simulated mailbox, calendar and Slack ----------
     A demo page carries live.demo: its mail threads, what the exec sent, today's events (an event
     marked `later` appears, one with `moved` moves, 1.5 s after opening), Slack DMs. Nothing is read
     or written anywhere: every reload replays it. Claude answers when the page may ask it; the
     demo's own answers stand in when it may not. */
  function memDb(){
    var m={}, self={};
    var docs=function(c){ return Object.keys(m).filter(function(k){ return k.indexOf(c+'/')===0; }).map(function(k){ return {id:k.slice(c.length+1), exists:true, metadata:{}, data:function(){ return JSON.parse(JSON.stringify(m[k])); }}; }); };
    self.doc=function(p){ return {id:p.split('/').pop(),
      get:async function(){ return {exists:p in m, id:p.split('/').pop(), data:function(){ return JSON.parse(JSON.stringify(m[p])); }}; },
      set:async function(v){ m[p]=JSON.parse(JSON.stringify(v)); },
      update:async function(v){ m[p]=Object.assign(m[p]||{},JSON.parse(JSON.stringify(v))); },
      delete:async function(){ delete m[p]; }}; };
    self.collection=function(c){ return {get:async function(){ return {docs:docs(c)}; },
      doc:function(id){ return self.doc(c+'/'+(id||('x'+Math.random().toString(36).slice(2,10)))); },
      onSnapshot:function(cb){ setTimeout(function(){ cb({docs:docs(c)}); },0); return function(){}; }}; };
    return self;
  }
  function demoMcp(){
    var D=DEMO, acct={alias:(D.account||{}).alias||'pro', email:(D.account||{}).email||''};
    var after=function(){ return Date.now()-T0>1500; };
    var at=function(hm){ var d=new Date(), p=String(hm).split(':'); d.setHours(+p[0],+p[1],0,0); return d.toISOString(); };
    var iso=function(x){ return /^\d{1,2}:\d{2}$/.test(String(x)) ? at(x) : x; };
    function threads(sent,q){
      var to=(String(q).match(/to:(\S+)/)||[])[1];
      return {threads:(D.mail||[]).filter(function(t){ return after()||!t.incoming; }).filter(function(t){
          if(!sent) return true;
          return (t.messages||[]).some(function(m){ return m.mine&&(after()||!m.later)&&(!to||String(m.to||'').toLowerCase().indexOf(to.toLowerCase())>=0); });
        }).map(function(t){
          var ms=(t.messages||[]).filter(function(x){ return after()||!x.later; }), m=ms[ms.length-1]||{};
          return {thread_id:t.id, subject:t.subject, from:m.from, date:iso(m.at), snippet:cut(m.body,200), unread:!m.mine, message_count:ms.length, account:acct}; })};
    }
    function events(){
      return {events:(D.events||[]).filter(function(e){ return after()||!e.later; }).map(function(e){
        var mv=after()&&e.moved ? e.moved : e;
        return {event_id:e.id, summary:e.title, start:at(mv.start), end:at(mv.end), all_day:false, status:after()&&e.cancelled?'cancelled':'confirmed',
          busy:true, my_response:'accepted', organizer:e.organizer||'', html_link:'', account:acct}; })};
    }
    function slack(){
      return {results:'# Results\n'+(D.slack||[]).filter(function(c){ return after()||!c.later; }).map(function(c,i){
        return '### Result '+(i+1)+'\nChannel: DM (ID: '+c.channel+')\nParticipants: '+(D.account||{}).name+' (ID: '+D.me_id+'), '+(c.peer||c.from)+' (ID: '+(c.peer_uid||c.uid)+')\nFrom: '+c.from+' (ID: '+c.uid+')\nTime: '+iso(c.at)
          +'\nMessage_ts: '+(Date.parse(iso(c.at))/1000).toFixed(6)+'\nPermalink: [link](#)\nText: \n'+c.text+'\n---\n'; }).join('')};
    }
    function payload(tool,input){
      if(tool==='gmail_search') return threads(/in:sent/.test(input.query||''),input.query||'');
      if(tool==='calendar_list_events') return events();
      if(tool==='slack_search_public_and_private') return slack();
      return {};
    }
    return {
      watchTool:function(server,tool,input,fn){
        setTimeout(function(){ fn({type:'data', result:{payload:payload(tool,input), cache:{storedAt:Date.now(), revalidating:true}}}); },0);
        setTimeout(function(){ fn({type:'data', result:{payload:payload(tool,input), cache:{storedAt:Date.now(), revalidating:false}}}); },1600);
        return function(){}; },
      invalidate:async function(){},
      callTool:async function(server,tool,input){
        await pause(300);
        if(tool==='gmail_search'||tool==='calendar_list_events'||tool==='slack_search_public_and_private') return {payload:payload(tool,input)};
        var t=(D.mail||[]).filter(function(x){ return x.id===(input&&(input.thread_id||input.reply_to_thread_id)); })[0];
        if(tool==='gmail_get_thread'&&t) return {payload:{messages:(t.messages||[]).filter(function(x){ return after()||!x.later; }).map(function(m){ return {from:m.from, date:iso(m.at), subject:t.subject, body:m.body}; })}};
        if(tool==='gmail_create_draft'||tool==='gmail_update_draft'){
          var last=t&&t.messages[t.messages.length-1];
          return {payload:{draft_token:input.draft_token||'demo', gmail_url:'', to:input.to&&input.to.length?input.to:(last?[addrOf(last.from)]:[])}}; }
        if(tool==='slack_read_channel'){ var c=(D.slack||[]).filter(function(y){ return y.channel===input.channel_id; })[0];
          return {payload:{messages:c ? (c.history||[]).concat([c.from+': '+c.text]).join('\n\n') : ''}}; }
        return {payload:{}};
      }
    };
  }

  /* ---------- boot: the page's capabilities, or the demo's stand-ins ---------- */
  K.boot=async function(){
    var use=function(n){ try{ return window.claude&&typeof window.claude.use==='function' ? window.claude.use(n) : Promise.resolve(null); }catch(e){ return Promise.resolve(null); } };
    if(DEMO){
      K.sample=await use('sample').catch(function(){ return null; });
      K.db=memDb(); K.mcp=demoMcp();
      return K;
    }
    var got=await Promise.allSettled([use('db'),use('mcp'),use('sample')]);
    K.db=got[0].value||null; K.mcp=got[1].value||null; K.sample=got[2].value||null;
    return K;
  };
  /* a watched read: the cached answer draws at once, the fresh one follows */
  K.watch=function(server,tool,input,onData,onError){
    var once=async function(){ try{ var r=await K.mcp.callTool(server,tool,input); onData(r.payload,true); }catch(e){ onError&&onError(e); } };
    try{
      return K.mcp.watchTool(server,tool,input,function(ev){
        if(ev.type==='data'){ var c=ev.result&&ev.result.cache; onData(ev.result.payload, !(c&&c.revalidating)); }
        else { var code=ev.error&&ev.error.code; if(code==='bad_request'||code==='capability_removed'||code==='capability_disabled'){ once(); return; } onError&&onError(ev.error); }
      },{cache:{staleTime:60000,gcTime:86400000}});
    }catch(e){ once(); return function(){}; }
  };
  return K;
}
