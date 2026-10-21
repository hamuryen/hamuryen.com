(() => {
  const panel = document.querySelector('.snake-panel');
  if (!panel || panel.hidden) return;
  const technologies = [
    ['cpp','C++'],['js','JavaScript'],['python','Python'],['qt','Qt'],['nodejs','Node.js'],
    ['csharp','C#'],['java','Java'],['spring','Spring Boot'],['k8s','Kubernetes'],['docker','Docker'],
    ['aws','AWS'],['gce','Google Cloud / GCE'],['azure','Azure'],['scala','Scala'],['kotlin','Kotlin'],
    ['go','Go'],['dotnet','ASP.NET Core'],['fastapi','FastAPI'],['terraform','Terraform'],
    ['prometheus','Prometheus'],['grafana','Grafana'],['postgresql','PostgreSQL'],['redis','Redis'],
    ['kafka','Kafka'],['elasticsearch','Elasticsearch'],['mongodb','MongoDB'],['k3s','K3s'],
    ['rtsp','RTSP'],['ai','AI'],['cloud','Cloud'],['zeromq','ZeroMQ'],['temporal','Temporal'],
    ['nats','NATS'],['pulsar','Pulsar'],['ffmpeg','FFmpeg'],['gstreamer','GStreamer'],
    ['deepstream','DeepStream'],['webrtc','WebRTC'],['onvif','ONVIF'],['live555','live555'],['gsoap','gSOAP'],
    ['boost','Boost.Asio'],['linux','Linux'],['centos','CentOS'],['helm','Helm'],
    ['kustomize','Kustomize'],['cuda','CUDA'],['nvidia','NVIDIA Orin'],['chromium','Chrome / Chromium'],
    ['rest','REST APIs'],['tcp','TCP'],['http','HTTP'],['upnp','UPnP'],['scada','SCADA'],['iot','IoT'],
    ['ios','iOS'],['android','Android'],['macos','macOS'],['windows','Windows'],['vscode','VS Code'],
    ['git','Git'],['github','GitHub'],['claude','Claude Code'],['cursor','Cursor'],['copilot','GitHub Copilot'],
    ['codex','Codex'],['playwright','Playwright'],['sentry','Sentry'],['notion','Notion'],
    ['npm','npm'],['mcp','MCP'],['context7','Context7']
  ];
  const dialog=document.querySelector('.snake-dialog');
  const preview=panel.querySelector('.snake-preview');
  const boards=[panel.querySelector('.snake-board'),dialog.querySelector('.snake-board')];
  const message=dialog.querySelector('.snake-message');
  const start=dialog.querySelector('.snake-start'), pause=dialog.querySelector('.snake-pause');
  const collected=dialog.querySelector('.snake-collected');
  const dirs={up:{x:0,y:-1},down:{x:0,y:1},left:{x:-1,y:0},right:{x:1,y:0}};
  const cols=20, rows=10;
  let snake, direction, pending, food, score, status='ready', timer, deck=[], earned=[];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const demoToggle = panel.querySelector('.snake-demo-toggle');
  let demoPaused = reduced.matches, visible = true, motionChosen = false;
  function svg(tag,attrs) {
    const node=document.createElementNS('http://www.w3.org/2000/svg',tag);
    Object.entries(attrs).forEach(([k,v])=>node.setAttribute(k,String(v)));return node;
  }
  function refill() {
    deck=technologies.map((_,i)=>i);
    for(let i=deck.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[deck[i],deck[j]]=[deck[j],deck[i]];}
  }
  function nextFood(initial=false) {
    if(!deck.length)refill();
    const free=[];
    for(let y=0;y<rows;y++)for(let x=0;x<cols;x++)if(!snake.some(p=>p.x===x&&p.y===y))free.push({x,y});
    if(!free.length){status='won';food=null;return;}
    food={...(initial?{x:10,y:5}:free[Math.floor(Math.random()*free.length)]),tech:deck.pop()};
  }
  function reset() {
    clearInterval(timer);snake=[{x:6,y:5},{x:5,y:5},{x:4,y:5},{x:3,y:5}];direction='right';pending=null;score=0;earned=[];status='ready';refill();nextFood(true);
    collected.replaceChildren();render();controls();
  }
  function render() {
    boards.forEach(board=>{
      const fragment=document.createDocumentFragment();
      for(let y=0;y<rows;y++)for(let x=0;x<cols;x++)fragment.appendChild(svg('circle',{cx:x*24+12,cy:y*24+12,r:1,class:'snake-grid-dot'}));
      snake.forEach((p,i)=>fragment.appendChild(svg('rect',{x:p.x*24+2,y:p.y*24+2,width:20,height:20,rx:5,class:i?'snake-segment':'snake-head'})));
      const head=snake[0],d=dirs[direction];
      [-1,1].forEach(side=>fragment.appendChild(svg('circle',{cx:head.x*24+12+d.x*5+(d.y?side*4:0),cy:head.y*24+12+d.y*5+(d.x?side*4:0),r:1.6,class:'snake-eye'})));
      if(food){fragment.appendChild(svg('rect',{x:food.x*24+1,y:food.y*24+1,width:22,height:22,rx:4,class:'snake-food-tile'}));fragment.appendChild(svg('image',{href:'assets/tech/'+technologies[food.tech][0]+'.svg',x:food.x*24+3,y:food.y*24+3,width:18,height:18}));}
      board.replaceChildren(fragment);
    });
    dialog.querySelector('#snake-score').textContent=score;
    dialog.querySelector('#snake-target').textContent=food?'Next: '+technologies[food.tech][1]:'All collected';
  }
  function controls() {
    pause.disabled=!['playing','paused'].includes(status);pause.querySelector('span').textContent=status==='paused'?'Resume':'Pause';
    pause.querySelector('path').setAttribute('d',status==='paused'?'m7 4 8 6-8 6Z':'M7 5v10M13 5v10');
    dialog.dataset.state=status;
    start.querySelector('span').textContent=status==='ready'?'Start game':'Restart';
    message.textContent={ready:'Ready when you are.',playing:'Cross the edges. Collect icons. Avoid your tail.',paused:'Paused. Resume when you’re ready.',over:'Game over. Give it another go.',won:'You filled the board!'}[status];
  }
  function schedule(){
    clearInterval(timer);
    if(document.hidden)return;
    if(dialog.open){if(status==='playing')timer=setInterval(step,180);}
    else if(!demoPaused&&visible)timer=setInterval(demoStep,240);
  }
  function demoStep(){
    if(!food||status==='over'||status==='won'||snake.length>24)reset();
    // Search for a free route to the next technology, rather than moving randomly.
    const blocked=new Set(snake.slice(0,-1).map(p=>p.x+','+p.y));
    const queue=[{...snake[0],first:null}],seen=new Set(blocked);
    let chosen;
    for(let i=0;i<queue.length;i++){
      const point=queue[i];
      if(point.x===food.x&&point.y===food.y){chosen=point.first;break;}
      for(const [name,d] of Object.entries(dirs)){
        if(!point.first&&d.x+dirs[direction].x===0&&d.y+dirs[direction].y===0)continue;
        const x=(point.x+d.x+cols)%cols,y=(point.y+d.y+rows)%rows,key=x+','+y;
        if(seen.has(key))continue;
        seen.add(key);queue.push({x,y,first:point.first||name});
      }
    }
    if(!chosen){reset();chosen='right';}
    pending=chosen;status='demo';step();schedule();
  }
  function turn(next){if(status!=='playing'||pending)return;const a=dirs[direction],b=dirs[next];if(a.x+b.x===0&&a.y+b.y===0)return;pending=next;}
  function step(){
    direction=pending||direction;pending=null;const d=dirs[direction],head={x:(snake[0].x+d.x+cols)%cols,y:(snake[0].y+d.y+rows)%rows};
    const eating=head.x===food.x&&head.y===food.y;
    const body=eating?snake:snake.slice(0,-1);
    if(body.some(p=>p.x===head.x&&p.y===head.y)){status='over';schedule();controls();return;}
    snake.unshift(head);
    if(eating){
      score++;const tech=technologies[food.tech];
      if(!earned.includes(food.tech)){earned.push(food.tech);const icon=document.createElement('img');icon.src='assets/tech/'+tech[0]+'.svg';icon.alt=tech[1];icon.title=tech[1];collected.appendChild(icon);}
      nextFood();if(dialog.open)message.textContent='Collected '+tech[1]+'.';
      if(status==='won'){schedule();controls();}
    }else snake.pop();
    render();
  }
  function togglePause(){if(!['playing','paused'].includes(status))return;status=status==='playing'?'paused':'playing';schedule();controls();}
  preview.addEventListener('click',()=>{clearInterval(timer);if(status==='over'||status==='won')reset();status='paused';pending=null;dialog.showModal();document.documentElement.classList.add('snake-open');controls();message.textContent='Your turn. Press Resume to take control, or Restart for a new game.';pause.focus();});
  start.addEventListener('click',()=>{reset();status='playing';controls();schedule();pause.focus();});
  pause.addEventListener('click',togglePause);
  dialog.querySelector('.snake-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',()=>{clearInterval(timer);status='ready';document.documentElement.classList.remove('snake-open');reset();schedule();preview.focus();});
  dialog.addEventListener('keydown',e=>{
    const map={ArrowUp:'up',ArrowDown:'down',ArrowLeft:'left',ArrowRight:'right',w:'up',s:'down',a:'left',d:'right'};
    const next=map[e.key]||map[e.key.toLowerCase()];
    if(next&&status==='playing'){e.preventDefault();turn(next);}else if(e.code==='Space'&&!e.target.closest('button')&&status!=='ready'&&!['over','won'].includes(status)){e.preventDefault();if(!e.repeat)togglePause();}
  });
  dialog.querySelectorAll('[data-dir]').forEach(button=>button.addEventListener('click',()=>turn(button.dataset.dir)));
  let touch;
  const arena=dialog.querySelector('.snake-arena');
  arena.addEventListener('pointerdown',e=>{touch={x:e.clientX,y:e.clientY};arena.setPointerCapture(e.pointerId);});
  arena.addEventListener('pointerup',e=>{if(!touch)return;const dx=e.clientX-touch.x,dy=e.clientY-touch.y;touch=null;if(Math.max(Math.abs(dx),Math.abs(dy))<12)return;turn(Math.abs(dx)>Math.abs(dy)?(dx>0?'right':'left'):(dy>0?'down':'up'));});
  arena.addEventListener('pointercancel',()=>{touch=null;});
  function suspend(){if(status==='playing'){status='paused';schedule();controls();}}
  document.addEventListener('visibilitychange',()=>{if(document.hidden)suspend();schedule();});window.addEventListener('blur',suspend);
  function updateDemo(){
    demoToggle.setAttribute('aria-label',demoPaused?'Play game preview':'Pause game preview');
    demoToggle.setAttribute('aria-pressed',String(demoPaused));
    demoToggle.querySelector('path').setAttribute('d',demoPaused?'M6 4l9 6-9 6z':'M7 5v10M13 5v10');
    schedule();
  }
  demoToggle.addEventListener('click',()=>{motionChosen=true;demoPaused=!demoPaused;updateDemo();});
  reduced.addEventListener('change',()=>{if(!motionChosen)demoPaused=reduced.matches;updateDemo();});
  if('IntersectionObserver' in window)new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;schedule();}).observe(panel);
  reset();updateDemo();
})();
