(() => {
  const panel = document.querySelector('.life-panel');
  if (!panel || panel.hidden) return;
  const field = panel.querySelector('.life-field');
  const toggle = panel.querySelector('.flow-toggle');
  const grid = field.querySelector('svg');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const cols = 32, rows = 14;
  let cells = new Uint8Array(cols * rows), paused = reduced.matches, visible = true, timer, generation = 0;
  const tiles = Array.from(cells, (_, i) => {
    const tile = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    Object.entries({x:16+i%cols*10,y:13+Math.floor(i/cols)*10,width:7,height:7,rx:1.5,class:'life-cell'}).forEach(([k,v])=>tile.setAttribute(k,v));
    panel.querySelector('.life-cells').appendChild(tile); return tile;
  });
  function plant(x,y) { [[1,0],[2,1],[0,2],[1,2],[2,2]].forEach(([dx,dy])=>{cells[((y+dy+rows)%rows)*cols+(x+dx+cols)%cols]=1;}); }
  function paint() { tiles.forEach((t,i)=>t.setAttribute('data-age',cells[i])); }
  plant(4,3);plant(21,7);plant(13,1);plant(10,8);paint();
  function step() {
    const next=new Uint8Array(cells.length);let alive=0;
    for(let y=0;y<rows;y++) for(let x=0;x<cols;x++) {
      let neighbors=0;
      for(let dy=-1;dy<=1;dy++) for(let dx=-1;dx<=1;dx++) if(dx||dy) neighbors+=cells[((y+dy+rows)%rows)*cols+(x+dx+cols)%cols]>0?1:0;
      const i=y*cols+x;
      if(neighbors===3||(cells[i]&&neighbors===2)){next[i]=Math.min(3,cells[i]+1);alive++;}
    }
    cells=next;generation++;if(alive<8||generation%48===0)plant(generation*7%29,generation*3%11);paint();
  }
  function update() {
    clearInterval(timer);if(!paused&&visible&&!document.hidden)timer=setInterval(step,480);
    toggle.hidden=reduced.matches;toggle.setAttribute('aria-pressed',String(paused));
    toggle.setAttribute('aria-label',paused?'Play illustration animation':'Pause illustration animation');
    toggle.querySelector('path').setAttribute('d',paused?'M6 4l9 6-9 6z':'M7 5v10M13 5v10');
  }
  field.addEventListener('click',e=>{
    let x=14,y=5;
    if(e.detail&&grid.getScreenCTM()) {const p=grid.createSVGPoint();p.x=e.clientX;p.y=e.clientY;const local=p.matrixTransform(grid.getScreenCTM().inverse());x=Math.max(0,Math.min(29,Math.floor((local.x-16)/10)-1));y=Math.max(0,Math.min(11,Math.floor((local.y-13)/10)-1));}
    plant(x,y);paint();
  });
  toggle.addEventListener('click',()=>{paused=!paused;update();});
  reduced.addEventListener('change',()=>{paused=reduced.matches;update();});
  document.addEventListener('visibilitychange',update);
  if('IntersectionObserver' in window)new IntersectionObserver(([e])=>{visible=e.isIntersecting;update();}).observe(panel);
  update();
})();
