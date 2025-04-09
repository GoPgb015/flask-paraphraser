function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.input-tab').forEach(tab => tab.classList.remove('active'));
    
    document.querySelector(`button[onclick="showTab('${tabName}')"]`).classList.add('active');
    document.getElementById(`${tabName}-input`).classList.add('active');
}

document.getElementById('paraphrase-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    fetch('/paraphrase', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        document.getElementById('original-text').textContent = data.original;
        document.getElementById('paraphrased-text').textContent = data.paraphrased;
        document.getElementById('result').classList.add('active');
    })
    .catch(error => console.error('Error:', error));
});