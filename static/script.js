async function fetchOutput() {
    const selectedOption = document.getElementById('outputSelect').value;
    const outputDiv = document.getElementById('outputArea');

    try {
        const response = await fetch(`/get_output/${selectedOption}`);
        const data = await response.json();

        outputDiv.innerHTML = ''; // Clear previous output

        if (data.type === 'image') {
            const img = document.createElement('img');
            img.src = data.url;
            img.style.maxWidth = '90%';
            outputDiv.appendChild(img);
        } else if (data.type === 'text') {
            const pre = document.createElement('pre');
            pre.textContent = data.content;
            outputDiv.appendChild(pre);
        } else {
            outputDiv.textContent = 'No data returned.';
        }
    } catch (err) {
        outputDiv.innerHTML = `<pre>Error: ${err}</pre>`;
    }
}
