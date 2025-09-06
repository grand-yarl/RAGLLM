        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileCount = document.getElementById('fileCount');
        const totalSize = document.getElementById('totalSize');
        const fileTypes = document.getElementById('fileTypes');
        const uploadForm = document.getElementById('uploadForm');

        // Обработка drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            dropZone.classList.add('dragover');
        }

        function unhighlight() {
            dropZone.classList.remove('dragover');
        }

        dropZone.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        fileInput.addEventListener('change', function() {
            handleFiles(this.files);
        });

        function handleFiles(files) {
            if (files.length === 0) return;

            // Обновляем информацию о файлах
            fileCount.textContent = files.length;

            let size = 0;
            const types = new Set();

            Array.from(files).forEach(file => {
                size += file.size;
                types.add(file.type || file.name.split('.').pop());
            });

            totalSize.textContent = formatFileSize(size);
            fileTypes.textContent = Array.from(types).join(', ');
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Б';
            const k = 1024;
            const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }