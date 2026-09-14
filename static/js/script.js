function toggleSidebar(){document.getElementById('sidebar')?.classList.toggle('open')}
function openModal(id){document.getElementById(id)?.classList.add('show')}
function closeModal(id){document.getElementById(id)?.classList.remove('show')}
window.addEventListener('click',e=>{if(e.target.classList.contains('modal'))e.target.classList.remove('show')})
function togglePassword(){const p=document.getElementById('password');if(p)p.type=p.type==='password'?'text':'password'}
function editBook(b){
  const form=document.getElementById('bookForm');
  document.getElementById('bookModalTitle').textContent='Edit Buku';
  form.action='/buku/edit/'+b.id;
  Object.keys(b).forEach(k=>{if(form.elements[k]) form.elements[k].value=b[k] ?? ''});
  openModal('bookModal');
}
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('.alert').forEach(el=>setTimeout(()=>{if(el.isConnected)el.remove()},4500));
  const due=document.querySelector('input[name="due_date"]');
  const loan=document.querySelector('input[name="loan_date"]');
  if(loan&&due&&!due.value){loan.addEventListener('change',()=>{const d=new Date(loan.value+'T00:00:00');d.setDate(d.getDate()+7);due.value=d.toISOString().slice(0,10)})}
});
