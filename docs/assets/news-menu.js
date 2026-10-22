// Shared news navigation. Local marks require no third-party image requests.
window.InvNewsMenu = (() => {
  const paths = {
    economy:'<path d="m4 9 8-5 8 5H4Zm1 12h14M7 11v7m5-7v7m5-7v7"/>',
    oil:'<path d="M8 4h8c3 5 3 11 0 16H8C5 15 5 9 8 4ZM6 8h12M6 16h12"/>',
    chip:'<rect x="7" y="7" width="10" height="10" rx="2"/><path d="M9 3v4m6-4v4M9 17v4m6-4v4M3 9h4m-4 6h4m10-6h4m-4 6h4"/>',
    health:'<rect x="4" y="6" width="16" height="15" rx="3"/><path d="M8 6V3h8v3m-4 5v6m-3-3h6"/>',
    consumer:'<path d="M6 8h12l2 13H4L6 8Zm3 0V6a3 3 0 0 1 6 0v2"/>',
    industry:'<path d="M3 21V9l6 4V8l6 4V3h5v18H3Zm3-4h2m3 0h2m3 0h2"/>',
    bond:'<path d="M6 3h9l4 4v14H6V3Zm9 0v5h4M9 12h7m-7 4h5"/>'
  };
  const svg = key => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[key] || paths.economy}</svg>`;
  const groups = {
    companies:['AAPL.svg','TSLA.svg','AMZN.png'], technology:['GOOGL.svg','MSFT.svg','NVDA.svg'],
    crypto:['BTC.svg','ETH.svg','SOL.svg'], stocks:['AAPL.svg','AMZN.png','TSLA.svg'], energy:['oil','XOM.png','SHEL.svg'], bonds:['bond','US','EU'], currencies:['€','$','¥']
  };
  function mark(key){
    const members=groups[key];
    if(members)return `<span class="nn-icon nn-cluster" aria-hidden="true">${members.map(m=>/\.(svg|png)$/.test(m)?`<img src="assets/logos/${m}" alt="" loading="lazy">`:paths[m]?`<span class="nn-mini">${svg(m)}</span>`:`<span class="nn-mini nn-symbol">${m}</span>`).join('')}</span>`;
    if(key==='indices')return '<span class="nn-icon nn-cluster" aria-hidden="true"><span class="nn-mini nn-symbol">NQ</span><span class="nn-mini nn-symbol">SPX</span><span class="nn-mini nn-symbol">DJI</span></span>';
    if(['europe','northamerica','asia','middleeast','africa','latinamerica'].includes(key))return `<span class="nn-icon nn-region" aria-hidden="true"><img src="assets/menu-icons/${key}.svg" alt="" loading="lazy"></span>`;
    return `<span class="nn-icon" aria-hidden="true">${svg(key)}</span>`;
  }
  const items = {
    Topics:[['Companies','companies','category','companies'],['Technology','technology','category','technology'],['Crypto','crypto','category','crypto'],['Economy','economy','category','economy'],['Commodities','oil','category','commodities'],['Geopolitics','europe','category','geopolitics']],
    Assets:[['Stocks','stocks','asset','stocks'],['Indices','indices','asset','indices'],['Oil & energy','energy','asset','energy'],['Bonds','bonds','asset','bonds'],['Currencies','currencies','asset','currencies'],['Crypto','crypto','asset','crypto']],
    Sectors:[['Technology','chip','sector','technology'],['Energy','oil','sector','energy'],['Financials','economy','sector','financials'],['Healthcare','health','sector','healthcare'],['Consumer','consumer','sector','consumer'],['Industrials','industry','sector','industrials']],
    Geography:[['Europe','europe','region','Europe'],['North America','northamerica','region','North America'],['Asia-Pacific','asia','region','Asia-Pacific'],['Middle East','middleeast','region','Middle East'],['Africa','africa','region','Africa'],['Latin America','latinamerica','region','Latin America']]
  };
  const content = group => `<p class="nn-heading">News by ${group.toLowerCase()}</p><div class="nn-items">${items[group].map(([label,key,param,value])=>`<a class="nn-item" href="news.html?${param}=${encodeURIComponent(value)}">${mark(key)}<span>${label}</span></a>`).join('')}</div>`;
  function html(id,initial='Topics'){return `<div class="nn-menu" data-news-menu><div class="nn-categories" role="group" aria-label="News filters">${Object.keys(items).map(g=>`<button type="button" data-news-group="${g}" aria-pressed="${g===initial}" aria-controls="${id}">${g}</button>`).join('')}</div><div class="nn-content" id="${id}">${content(initial)}</div><div class="nn-foot"><span>Browse financial news</span><a href="news.html">All news →</a></div></div>`;}
  document.addEventListener('click',e=>{const b=e.target.closest('[data-news-group]');if(!b)return;const root=b.closest('[data-news-menu]');root.querySelectorAll('[data-news-group]').forEach(t=>t.setAttribute('aria-pressed',String(t===b)));root.querySelector('.nn-content').innerHTML=content(b.dataset.newsGroup);});
  document.addEventListener('error',e=>{if(e.target instanceof HTMLImageElement&&e.target.closest('.nn-icon'))e.target.remove();},true);
  function matches(story, params, markets=[]) {
    const category=params.get('category'),region=params.get('region'),asset=params.get('asset'),sector=params.get('sector');
    if(category && story.category!==category)return false;
    if(region){const codes={'Europe':['eu'],'North America':['na'],'Asia-Pacific':['asia','oc'],'Middle East':['me'],'Africa':['af'],'Latin America':['latam']};if(!(codes[region]||[]).includes(story.location?.region))return false;}
    const entities=[...(story.entities||[]),...(story.impacts||[])],symbols=entities.map(e=>e.ticker).filter(Boolean),known=markets.filter(a=>symbols.includes(a.s));
    const text=[story.headline,story.summary,...entities.map(e=>e.name)].join(' ').toLowerCase();
    if(asset){const types={stocks:()=>known.some(a=>a.t==='stocks'&&!/^\^/.test(a.s)&&a.g!=='Index')||symbols.some(s=>!/[-=^]/.test(s)),indices:()=>known.some(a=>a.g==='Index')||symbols.some(s=>/^\^|^(NQ|ES|YM)=/.test(s)),energy:()=>known.some(a=>a.g==='Energy')||/\b(oil|crude|brent|wti|natural gas|energy|petroleum)\b/.test(text),bonds:()=>/\b(bonds?|treasur(?:y|ies)|gilts?|bunds?|fixed.income)\b/.test(text),currencies:()=>known.some(a=>a.t==='fx')||symbols.some(s=>/=X$/.test(s))||/\b(currencies|currency|forex|euro|yen|dollar|sterling)\b/.test(text),crypto:()=>story.category==='crypto'||symbols.some(s=>/-USD$/.test(s))};if(!types[asset]?.())return false;}
    if(sector){const names={technology:['Technology','Communication'],energy:['Energy','Utilities'],financials:['Finance'],healthcare:['Healthcare'],consumer:['Consumer'],industrials:['Industrials']};const words={technology:/\b(technology|software|semiconductor|chips?|artificial intelligence)\b/,energy:/\b(oil|gas|energy|petroleum|power)\b/,financials:/\b(banks?|banking|insurers?|financial services)\b/,healthcare:/\b(healthcare|pharma|medical|drug|biotech)\b/,consumer:/\b(retail|consumer|brands|supermarket)\b/,industrials:/\b(manufactur|industrial|aerospace|transport|aviation)/};if(!known.some(a=>(names[sector]||[]).includes(a.g))&&!words[sector]?.test(text))return false;}
    return true;
  }
  return {html,matches};
})();
