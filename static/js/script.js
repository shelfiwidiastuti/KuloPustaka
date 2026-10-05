function toggleSidebar(){
    document.getElementById('sidebar')?.classList.toggle('open');
}

function openModal(id){
    document.getElementById(id)?.classList.add('show');
}

function closeModal(id){
    document.getElementById(id)?.classList.remove('show');
}

window.addEventListener('click', e => {
    if(e.target.classList.contains('modal')){
        e.target.classList.remove('show');
    }
});

function togglePassword(){
    const p = document.getElementById('password');

    if(p){
        p.type = p.type === 'password' ? 'text' : 'password';
    }
}

function editBook(b){
    const form = document.getElementById('bookForm');

    document.getElementById('bookModalTitle').textContent = 'Edit Buku';

    form.action = '/buku/edit/' + b.id;

    Object.keys(b).forEach(k => {
        if(form.elements[k]){
            form.elements[k].value = b[k] ?? '';
        }
    });

    openModal('bookModal');
}


document.addEventListener('DOMContentLoaded', () => {

    /* =========================
       ALERT OTOMATIS HILANG
    ========================== */
    document.querySelectorAll('.alert').forEach(el => {
        setTimeout(() => {
            if(el.isConnected){
                el.remove();
            }
        }, 4500);
    });


    /* =========================
       PARAF / TANDA TANGAN
    ========================== */

    const signatureCanvas = document.getElementById('signatureCanvas');
    const signatureInput = document.getElementById('guestParaf');
    const clearSignature = document.getElementById('clearSignature');

    // Jalankan hanya jika elemen paraf memang ada
    if(signatureCanvas && signatureInput){

        const ctx = signatureCanvas.getContext('2d');

        let drawing = false;


        /* Mendapatkan posisi mouse/touch
           sesuai ukuran canvas */
        function getSignaturePosition(event){

            const rect = signatureCanvas.getBoundingClientRect();

            const scaleX =
                signatureCanvas.width / rect.width;

            const scaleY =
                signatureCanvas.height / rect.height;

            return {
                x: (event.clientX - rect.left) * scaleX,
                y: (event.clientY - rect.top) * scaleY
            };
        }


        /* Mulai menggambar */
        signatureCanvas.addEventListener(
            'pointerdown',
            function(event){

                drawing = true;

                const pos =
                    getSignaturePosition(event);

                ctx.beginPath();

                ctx.moveTo(
                    pos.x,
                    pos.y
                );

                signatureCanvas.setPointerCapture(
                    event.pointerId
                );
            }
        );


        /* Saat mouse/jari digerakkan */
        signatureCanvas.addEventListener(
            'pointermove',
            function(event){

                if(!drawing) return;

                const pos =
                    getSignaturePosition(event);

                ctx.lineWidth = 2;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';

                ctx.lineTo(
                    pos.x,
                    pos.y
                );

                ctx.stroke();
            }
        );


        /* Selesai menggambar */
        signatureCanvas.addEventListener(
            'pointerup',
            function(){

                drawing = false;

                saveSignature();
            }
        );


        signatureCanvas.addEventListener(
            'pointercancel',
            function(){

                drawing = false;
            }
        );


        /* Simpan gambar paraf ke input hidden */
        function saveSignature(){

            signatureInput.value =
                signatureCanvas.toDataURL('image/png');
        }


        /* Hapus paraf */
        function clearSignatureCanvas(){

            ctx.clearRect(
                0,
                0,
                signatureCanvas.width,
                signatureCanvas.height
            );

            signatureInput.value = '';
        }


        /* Tombol Hapus Paraf */
        if(clearSignature){

            clearSignature.addEventListener(
                'click',
                clearSignatureCanvas
            );
        }


        /* Pastikan paraf tersimpan sebelum form dikirim */
        const guestForm =
            signatureCanvas.closest('form');

        if(guestForm){

            guestForm.addEventListener(
                'submit',
                function(){

                    saveSignature();
                }
            );
        }
    }


    /* =========================
       TANGGAL JATUH TEMPO
    ========================== */

    const due =
        document.querySelector('input[name="due_date"]');

    const loan =
        document.querySelector('input[name="loan_date"]');

    if(
        loan &&
        due &&
        !due.value
    ){

        loan.addEventListener(
            'change',
            () => {

                const d =
                    new Date(
                        loan.value + 'T00:00:00'
                    );

                d.setDate(
                    d.getDate() + 7
                );

                due.value =
                    d.toISOString().slice(0, 10);
            }
        );
    }

});