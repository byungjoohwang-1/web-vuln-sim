/**
 * WEB-VULN-SIM Client-Side SAST & Lexical Analysis Engine
 * Used for advanced validation of secure coding practices.
 */
window.sastEngine = {
    tokenizeJava: function(code) {
        // String-literal aware comment stripping
        const commentRegex = /"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|(\/\/.*|\/\*[\s\S]*?\*\/)/g;
        let cleaned = code.replace(commentRegex, (m, g1) => g1 ? "" : m);
        
        const tokens = [];
        const regex = /"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b\w+\b|[^\s\w]/g;
        let match;
        while ((match = regex.exec(cleaned)) !== null) {
            tokens.push(match[0]);
        }
        return tokens;
    },

    tokenizePython: function(code) {
        // String-literal aware comment stripping
        const commentRegex = /[fF]?"(?:\\.|[^"\\])*"|[fF]?'(?:\\.|[^'\\])*'|(#.*|"""[\s\S]*?"""|'''[\s\S]*?''')/g;
        let cleaned = code.replace(commentRegex, (m, g1) => g1 ? "" : m);
        
        const tokens = [];
        const regex = /[fF]?"(?:\\.|[^"\\])*"|[fF]?'(?:\\.|[^'\\])*'|\b\w+\b|[^\s\w]/g;
        let match;
        while ((match = regex.exec(cleaned)) !== null) {
            tokens.push(match[0]);
        }
        return tokens;
    },

    hasToken: function(tokens, target) {
        return tokens.includes(target);
    },

    hasTokenSequence: function(tokens, sequence) {
        for (let i = 0; i <= tokens.length - sequence.length; i++) {
            let match = true;
            for (let j = 0; j < sequence.length; j++) {
                if (tokens[i + j] !== sequence[j]) {
                    match = false;
                    break;
                }
            }
            if (match) return true;
        }
        return false;
    },

    getJavaStringLiterals: function(code) {
        const commentRegex = /"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|(\/\/.*|\/\*[\s\S]*?\*\/)/g;
        let cleaned = code.replace(commentRegex, (m, g1) => g1 ? "" : m);
        const literals = [];
        const regex = /"(?:\\.|[^"\\])*"/g;
        let match;
        while ((match = regex.exec(cleaned)) !== null) {
            literals.push(match[0]);
        }
        return literals;
    },

    getPythonStringLiterals: function(code) {
        const commentRegex = /[fF]?"(?:\\.|[^"\\])*"|[fF]?'(?:\\.|[^'\\])*'|(#.*|"""[\s\S]*?"""|'''[\s\S]*?''')/g;
        let cleaned = code.replace(commentRegex, (m, g1) => g1 ? "" : m);
        const literals = [];
        const regex = /[fF]?"(?:\\.|[^"\\])*"|[fF]?'(?:\\.|[^'\\])*'/g;
        let match;
        while ((match = regex.exec(cleaned)) !== null) {
            literals.push(match[0]);
        }
        return literals;
    }
};

// Auto-Sync Lab Progress to LocalStorage
(function() {
    function checkProgress() {
        const path = window.location.pathname;
        const filename = path.split('/').pop().replace('.html', '');
        if (!filename.startsWith('03_code_')) return;

        // Check for elements with secure status
        const badges = document.querySelectorAll('.status-badge, [id*="status" i], [id*="Status" i], [id^="stJ" i], [id^="stP" i], [id^="st" i]');
        badges.forEach(badge => {
            if (badge.classList.contains('status-secure') || badge.textContent.includes('안전') || badge.textContent.toLowerCase().includes('secure')) {
                const id = badge.id.toLowerCase();
                const isJava = id.includes('java') || id.includes('stj') || id.includes('stjava') || id.includes('st-java') || badge.closest('#java-mode, .java-mode') !== null;
                const isPython = id.includes('python') || id.includes('py') || id.includes('stp') || id.includes('stpy') || id.includes('stpython') || badge.closest('#python-mode, .python-mode') !== null;
                
                if (isJava) {
                    localStorage.setItem(`wvs_passed_${filename}_java`, 'true');
                }
                if (isPython) {
                    localStorage.setItem(`wvs_passed_${filename}_python`, 'true');
                }
                if (!isJava && !isPython) {
                    // Fallback for single-language pages or unspecified badges
                    localStorage.setItem(`wvs_passed_${filename}_java`, 'true');
                    localStorage.setItem(`wvs_passed_${filename}_python`, 'true');
                }
            }
        });
    }

    if (typeof window !== 'undefined') {
        window.addEventListener('DOMContentLoaded', () => {
            checkProgress();
            setInterval(checkProgress, 1000);
        });
    }
})();
