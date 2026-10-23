const $ = (id) => document.getElementById(id);
let monthlyChart, yearlyChart, latestFile = null;
const chartDefaults = { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false},tooltip:{backgroundColor:'#173652',padding:11,displayColors:false,titleFont:{family:'DM Sans',size:11},bodyFont:{family:'DM Sans',size:11},callbacks:{label:(ctx)=>` ${Number(ctx.raw).toLocaleString()} mm`}},}, scales:{x:{grid:{display:false},border:{display:false},ticks:{color:'#9aabba',font:{family:'DM Sans',size:10}}},y:{beginAtZero:true,grid:{color:'#edf2f7',drawTicks:false},border:{display:false},ticks:{color:'#a1afbd',padding:9,font:{family:'DM Sans',size:9}}}}};
function makeCharts(data){
  const mctx=$('monthlyChart').getContext('2d');
  const grad=mctx.createLinearGradient(0,0,0,230);grad.addColorStop(0,'rgba(57,148,218,.27)');grad.addColorStop(1,'rgba(57,148,218,.015)');
  if(monthlyChart) monthlyChart.destroy();
  monthlyChart=new Chart(mctx,{type:'line',data:{labels:data.monthly_labels,datasets:[{data:data.monthly_values,borderColor:'#3b94da',backgroundColor:grad,fill:true,tension:.42,borderWidth:2.5,pointRadius:3,pointHoverRadius:6,pointBackgroundColor:'#fff',pointBorderColor:'#3b94da',pointBorderWidth:2}]},options:{...chartDefaults,interaction:{intersect:false,mode:'index'}}});
  if(yearlyChart) yearlyChart.destroy();
  yearlyChart=new Chart($('yearlyChart').getContext('2d'),{type:'bar',data:{labels:data.year_labels,datasets:[{data:data.year_values,backgroundColor:data.year_labels.map((_,i)=>i===data.year_labels.length-1?'#3d97db':'#cce7fa'),borderRadius:5,borderSkipped:false,maxBarThickness:33}]},options:{...chartDefaults,scales:{...chartDefaults.scales,x:{...chartDefaults.scales.x,ticks:{...chartDefaults.scales.x.ticks,maxRotation:0}},y:{...chartDefaults.scales.y,ticks:{...chartDefaults.scales.y, maxTicksLimit:4}}}}});
}
function intensity(mm){if(mm===0)return ['Dry',''];if(mm<10)return ['Light','light'];if(mm<35)return ['Moderate','moderate'];if(mm<65)return ['Heavy','heavy'];return ['Very heavy','veryheavy'];}
function render(data){
  $('totalValue').textContent=Number(data.total).toLocaleString(undefined,{maximumFractionDigits:2});
  $('avgValue').textContent=Number(data.average).toLocaleString(undefined,{maximumFractionDigits:2});
  $('maxValue').textContent=Number(data.max_day).toLocaleString(undefined,{maximumFractionDigits:2});
  $('maxDate').textContent=data.max_date;
  $('rainyValue').textContent=data.rainy_days;
  $('dryText').textContent=`Dry days: ${data.dry_days}`;
  $('heroTotal').innerHTML=`${Number(data.total).toLocaleString(undefined,{maximumFractionDigits:1})} <small>mm</small>`;
  $('heroRainy').textContent=data.rainy_days;
  $('heroLocation').textContent=(data.location_labels||[]).length===1?data.location_labels[0]:'Multiple stations';
  $('meterFill').style.width=`${Math.max(8,Math.min(100,data.total/Math.max(data.total,500)*100))}%`;
  $('recordCount').textContent=`${data.records} records`;
  $('sourceLabel').textContent=`Source: ${data.source||'sample_rainfall.csv'}`;
  $('insightText').textContent=data.insight||`Your dataset contains ${data.records} valid records. Peak rainfall reached ${data.max_day} mm on ${data.max_date}.`;
  const body=$('recordsBody');body.innerHTML='';
  (data.table||[]).forEach(row=>{
    const [label,cls]=intensity(Number(row.rainfall_mm));
    const pct=Math.min(100,Number(row.rainfall_mm)/Math.max(1,data.max_day)*100);
    const tr=document.createElement('tr');
    tr.innerHTML=`<td>${escapeHtml(row.date)}</td><td>${escapeHtml(row.location)}</td><td><span class="rain-badge">${Number(row.rainfall_mm).toLocaleString()} mm</span></td><td><div class="intensity"><div class="intensity-bar"><i style="width:${pct}%"></i></div><small>${label}</small></div></td>`;
    body.appendChild(tr);
  });
  makeCharts(data);
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
async function analyze(file=null){
  const form=new FormData();if(file)form.append('file',file);
  $('analyzeBtn').disabled=true;$('analyzeBtn').textContent='Analyzing…';
  try{
    const res=await fetch('/api/analyze',{method:'POST',body:form});
    const data=await res.json();if(!res.ok)throw new Error(data.error||'Could not analyze the file.');
    render(data);showToast(`Analysis complete · ${data.records} valid records found.`);
  }catch(e){showToast(e.message||'Something went wrong.');}
  finally{$('analyzeBtn').disabled=false;$('analyzeBtn').innerHTML='Analyze data <span>↗</span>';}
}
function showToast(msg){const t=$('toast');t.textContent=msg;t.classList.add('show');clearTimeout(window.toastTimer);window.toastTimer=setTimeout(()=>t.classList.remove('show'),3300);}
$('csvFile').addEventListener('change',e=>{latestFile=e.target.files[0]||null;$('fileLabel').textContent=latestFile?latestFile.name:'Choose CSV file';});
$('uploadForm').addEventListener('submit',e=>{e.preventDefault();if(!latestFile){showToast('Choose a CSV file first, or use the sample dataset.');return;}analyze(latestFile);});
$('sampleBtn').addEventListener('click',()=>{latestFile=null;$('csvFile').value='';$('fileLabel').textContent='Choose CSV file';analyze();});
$('downloadBtn').addEventListener('click',async()=>{
  const form=new FormData();if(latestFile)form.append('file',latestFile);
  try{const res=await fetch('/download-report',{method:'POST',body:form});if(!res.ok){const e=await res.json();throw new Error(e.error||'Report export failed.');}
  const blob=await res.blob();const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='rainfall_analysis_report.xlsx';a.click();URL.revokeObjectURL(url);showToast('Your Excel report is ready.');}
  catch(e){showToast(e.message||'Could not export report.');}
});
function createRain(){
  const layer=$('rainLayer');for(let i=0;i<48;i++){const line=document.createElement('i');line.className='rain-line';line.style.left=(Math.random()*100)+'%';line.style.animationDuration=(1.3+Math.random()*2.5)+'s';line.style.animationDelay=(-Math.random()*4)+'s';line.style.opacity=(.18+Math.random()*.4);line.style.height=(15+Math.random()*23)+'px';layer.appendChild(line);}
}
$('rainToggle').addEventListener('click',()=>{const layer=$('rainLayer');layer.classList.toggle('paused');showToast(layer.classList.contains('paused')?'Rain animation paused.':'Rain animation enabled.');});
createRain();
fetch('/api/analyze',{method:'POST'}).then(r=>r.json()).then(d=>{if(!d.error)render(d);}).catch(()=>showToast('Could not load sample data. Check that the Python server is running.'));
