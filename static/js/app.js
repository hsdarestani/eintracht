(function(){
  const menuButton=document.querySelector('[data-menu]');
  const sidebar=document.getElementById('sidebar');
  if(menuButton&&sidebar){menuButton.addEventListener('click',()=>sidebar.classList.toggle('open'));document.addEventListener('click',e=>{if(window.innerWidth<=860&&!sidebar.contains(e.target)&&!menuButton.contains(e.target))sidebar.classList.remove('open')})}

  document.querySelectorAll('input[type="range"]').forEach(input=>{
    const output=document.querySelector(`[data-output-for="${input.id}"]`);
    const sync=()=>{if(output)output.textContent=input.value}; sync(); input.addEventListener('input',sync)
  });

  const csrf=()=>{const item=document.cookie.split('; ').find(row=>row.startsWith('csrftoken='));return item?decodeURIComponent(item.split('=')[1]):''};
  document.querySelectorAll('[data-attendance]').forEach(group=>{
    group.querySelectorAll('button').forEach(button=>button.addEventListener('click',async()=>{
      const status=document.querySelector('[data-save-status]'); if(status){status.textContent='Wird gespeichert …';status.className='save-status saving'}
      const body=new URLSearchParams({action:'attendance',attendance_id:group.dataset.id,status:button.dataset.value});
      try{const response=await fetch(group.dataset.url,{method:'POST',headers:{'X-CSRFToken':csrf(),'X-Requested-With':'XMLHttpRequest'},body});if(!response.ok)throw new Error();group.querySelectorAll('button').forEach(x=>x.classList.remove('active'));button.classList.add('active');if(status){status.textContent='Gespeichert';status.className='save-status saved';setTimeout(()=>{status.textContent='Änderungen werden sofort gespeichert';status.className='save-status'},1600)}}catch(e){if(status){status.textContent='Speichern fehlgeschlagen';status.className='save-status saving'}}
    }))
  });

  setTimeout(()=>document.querySelectorAll('.message').forEach(x=>x.remove()),4000);
})();
