# -*- coding: utf-8 -*-
import sys
import os
import re
import time
import json
import importlib

sys.stdout.reconfigure(encoding='utf-8')

# Custom compile_one using C++14
def compile_one_cpp14(code):
    import urllib.request
    body = json.dumps({
        'code': code,
        'compiler': 'gcc-13.2.0',
        'options': 'warning',
        'compiler-option-raw': '-std=gnu++14\n-pthread',
        'stdin': ''
    }).encode('utf-8')
    
    last = ''
    for attempt in range(4):
        try:
            req = urllib.request.Request(
                'https://wandbox.org/api/compile.json',
                data=body,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (compile-verify)'
                }
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                j = json.loads(r.read().decode('utf-8'))
            err = (j.get('compiler_error') or '')
            err_lines = [l for l in err.splitlines() if 'error:' in l]
            ok = len(err_lines) == 0
            return ok, (err_lines[0] if err_lines else '')
        except Exception as e:
            last = str(e)
            time.sleep(1.5 * (attempt + 1))
    return False, 'REQUEST_FAILED: ' + last

# Import std_autosar_extracted
sys.path.append('.')
import std_autosar_extracted

def fix_curly_quotes(code):
    replacements = {
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'",
        '•': '*',
        '–': '-',
        '—': '-',
        '\uFFFD': "'", # Fix PDF encoding replacement chars
    }
    for k, v in replacements.items():
        code = code.replace(k, v)
    return code

def fix_multiline_strings(code):
    lines = code.splitlines()
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        quotes = len(re.findall(r'(?<!\\)"', line))
        if quotes % 2 != 0 and i + 1 < len(lines):
            line = line + " " + lines[i+1].lstrip()
            i += 2
            quotes = len(re.findall(r'(?<!\\)"', line))
            while quotes % 2 != 0 and i < len(lines):
                line = line + " " + lines[i].lstrip()
                i += 1
                quotes = len(re.findall(r'(?<!\\)"', line))
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
            i += 1
    return "\n".join(fixed_lines)

def fix_wrapped_comments(code):
    lines = code.splitlines()
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # If this line has a comment
        if '//' in line and i + 1 < len(lines):
            next_line = lines[i+1]
            next_strip = next_line.strip()
            # If the next line has text but does not look like C++ code
            if next_strip and not next_strip.startswith('//') and not next_strip.startswith('/*') and not next_strip.startswith('#'):
                # Check if it has no code punctuation, or contains comment keywords
                is_text = (
                    ';' not in next_strip and
                    '{' not in next_strip and
                    '}' not in next_strip and
                    '=' not in next_strip and
                    '(' not in next_strip and
                    ')' not in next_strip
                ) or any(w in next_strip.lower() for w in ['compliant', 'ctor', 'dtor', 'parameter', 'exception', 'constructor', 'destructor', 'function', 'object', 'recommended', 'defined'])
                
                if is_text:
                    lines[i+1] = '// ' + next_line.lstrip()
        fixed_lines.append(lines[i])
        i += 1
    return "\n".join(fixed_lines)

def fix_pure_virtual_destructors(code):
    # virtual ~ClassName() = 0; -> virtual ~ClassName() {}
    return re.sub(r'virtual\s+~([A-Za-z0-9_]+)\s*\(\s*\)\s*=\s*0\s*;', r'virtual ~\1() {}', code)

def comment_out_text_only(code, rid):
    stripped = code.strip()
    if stripped.startswith('//') or stripped.startswith('/*'):
        return code
        
    cpp_prefixes = (
        '#', 'class', 'struct', 'template', 'using', 'namespace',
        'typedef', 'extern', 'void', 'int', 'bool', 'double', 'float', 'char',
        'std::', 'const', 'constexpr', 'inline', 'static', 'auto', 'enum',
        'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t', 'int8_t', 'int16_t', 'int32_t', 'int64_t'
    )
    
    first_line = stripped.splitlines()[0].strip()
    first_word = first_line.split()[0].lower() if first_line.split() else ''
    first_word_clean = re.sub(r'[^a-z0-9_#]', '', first_word)
    
    is_cpp = (
        any(first_line.startswith(p) for p in cpp_prefixes) or
        any(first_word_clean == p for p in cpp_prefixes)
    )
    
    if not is_cpp:
        lines = code.splitlines()
        commented = [f"// {line}" for line in lines]
        return "\n".join(commented)
    return code

def is_comment_only(code):
    lines = code.strip().splitlines()
    if not lines:
        return True
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        if not (line_str.startswith('//') or line_str.startswith('/*') or line_str.startswith('*') or line_str.endswith('*/')):
            return False
    return True

def inject_missing_headers(code):
    mapping = {
        r'\b(u?int(8|16|32|64)_t)\b': '<cstdint>',
        r'\b(std::)?(vector)\b': '<vector>',
        r'\b(std::)?(array)\b': '<array>',
        r'\b(std::)?(initializer_list)\b': '<initializer_list>',
        r'\b(std::)?(string)\b': '<string>',
        r'\b(std::)?(shared_ptr|unique_ptr|make_shared|make_unique)\b': '<memory>',
        r'\b(std::)?(cout|cin|endl)\b': '<iostream>',
        r'\b(std::)?(sqrt|log|sin|cos|tan|pow|abs)\b': '<cmath>',
        r'\b(size_t|ptrdiff_t|nullptr_t)\b': '<cstddef>',
        r'\b(std::)?(map|unordered_map)\b': '<map>',
        r'\b(std::)?(set|unordered_set)\b': '<set>',
        r'\b(std::)?(find|sort|max|min)\b': '<algorithm>',
        r'\b(std::)?(move|forward|pair|make_pair)\b': '<utility>',
        r'\b(std::)?(exception|runtime_error|invalid_argument)\b': '<stdexcept>',
        r'\b(std::)?(thread)\b': '<thread>',
        r'\b(std::)?(mutex|lock_guard|unique_lock)\b': '<mutex>',
    }
    
    headers_to_add = []
    for pattern, header in mapping.items():
        if re.search(pattern, code):
            include_pattern = rf'#include\s+["<]{re.escape(header.strip("<>"))}[">]'
            if not re.search(include_pattern, code):
                headers_to_add.append(header)
                
    if headers_to_add:
        header_lines = "\n".join(f"#include {h}" for h in headers_to_add) + "\n"
        code = header_lines + "\n" + code
    return code

def apply_rule_patches(rid, code):
    patches = {
        'A3-3-1': [
            ('#include "A3-3-1.hpp"', '// #include "A3-3-1.hpp"')
        ],
        'A3-8-1': [
            ('std::out', 'std::cout'),
            ('new (&a) std::vector<int>{};', 'new (&str) std::vector<int>{};')
        ],
        'A5-0-2': [
            ('extern std::int32_t * Fn();', 'std::int32_t * Fn() { return nullptr; }'),
            ('extern std::int32_t Fn2();', 'std::int32_t Fn2() { return 0; }'),
            ('extern bool Fn3();', 'bool Fn3() { return false; }')
        ],
        'A5-0-4': [
            ('virtual ~Base() noexcept = 0;', 'virtual ~Base() noexcept {}')
        ],
        'A5-1-7': [
            ('void Foo(T t);', 'void Foo(T t) {}')
        ],
        'A5-2-1': [
            ('virtual void F() noexcept;', 'virtual void F() noexcept {}')
        ],
        'A7-3-1': [
            ('virtual void V(uint32_t);', 'virtual void V(uint32_t) {}'),
            ('virtual void V(double);', 'virtual void V(double) {}')
        ],
        'A8-4-6': [
            ('explicit A(std::vector<std::string> &&v);', 'explicit A(std::vector<std::string> &&v) {}'),
            ('explicit B(const std::vector<std::string> &v);', 'explicit B(const std::vector<std::string> &v) {}')
        ],
        'A8-4-11': [
            ('void do_stuff();', 'void do_stuff() {}')
        ],
        'A13-5-5': [
            ('operator A() const;', 'operator A() const { return A(0); }'),
            ('operator B() const;', 'operator B() const { return B(0); }')
        ],
        'A14-5-3': [
            ('bool operator+( long rhs );', 'bool operator+( long rhs ) { return true; }')
        ],
        'A15-0-1': [
            ('std::uint8_t ComputeCrc(std::string& msg);', 'std::uint8_t ComputeCrc(std::string& msg) { return 0; }')
        ],
        'A15-1-4': [
            ('extern std::uint32_t F1();', 'std::uint32_t F1() { return 0; }')
        ],
        'A15-3-2': [
            ('extern void Send(std::uint8_t * buffer) noexcept(false);', 'void Send(std::uint8_t * buffer) noexcept(false) {}'),
            ('extern void BusRestart() noexcept;', 'void BusRestart() noexcept {}'),
            ('extern void BufferClean() noexcept;', 'void BufferClean() noexcept {}'),
            ('extern void Cleanup() noexcept;', 'void Cleanup() noexcept {}')
        ],
        'A15-3-4': [
            ('extern std::int32_t Fn();', 'std::int32_t Fn() { return 0; }')
        ],
        'A15-4-1': [
            ('void F5() throw(\n...); // Non-compliant - dynamic exception-specification is deprecated', '#if 0\nvoid F5() throw(...);\n#endif // Non-compliant')
        ],
        'A15-4-3': [
            ('void Fn() noexcept(false) // Non-compliant', 'void Fn_bad() noexcept(false) // Non-compliant')
        ],
        'A15-5-2': [
            ('void F1() noexcept(false);', 'void F1() noexcept(false) {}')
        ],
        'A15-5-3': [
            ('extern bool F1();', 'bool F1() { return true; }')
        ],
        'A16-2-3': [
            ('#include <array>', '#include <array>\n#include <stdexcept>')
        ],
        'A18-1-4': [
            ('std::shared_ptr<A> sp{up.release()}; // Non-compliant', '#if 0\nstd::shared_ptr<A> sp{up.release()};\n#endif // Non-compliant'),
            ('sp.reset(up.release()); // Non-compliant', '#if 0\nsp.reset(up.release());\n#endif // Non-compliant'),
            ('std::shared_ptr<A> sp{std::move(up)}; // Non-compliant\nsp.reset(new A{}); // leads to undefined behavior', '#if 0\nstd::shared_ptr<A> sp{std::move(up)};\nsp.reset(new A{});\n#endif // Non-compliant'),
            ('std::shared_ptr<A> sp{up.release(),\nstd::default_delete<A[]>{}}; // Non-compliant\nsp.reset(new A{}); // leads to undefined behavior', '#if 0\nstd::shared_ptr<A> sp{up.release(),\nstd::default_delete<A[]>{}};\nsp.reset(new A{});\n#endif // Non-compliant')
        ],
        'A18-5-9': [
            ('extern void * custom_alloc(std::size_t); // Implemented elsewhere; may return', 'void * custom_alloc(std::size_t) { return nullptr; } // Implemented elsewhere; may return')
        ],
        'A2-13-6': [
            ('void \\U0001f615()\n{\n//\n}', '#if 0\nvoid \\U0001f615()\n{\n}\n#endif')
        ]
    }
    
    if rid in patches:
        for target, replacement in patches[rid]:
            code = code.replace(target, replacement)
            
    return code

print(f"Loaded {len(std_autosar_extracted.RULES)} rules from std_autosar_extracted.py")

cleaned_rules = []
for i, r in enumerate(std_autosar_extracted.RULES):
    rid = r['id']
    code = r['bad']
    
    # 1. Clean quotes & encoding
    code = fix_curly_quotes(code)
    
    # 2. Fix multiline strings
    code = fix_multiline_strings(code)
    
    # 3. Comment out text-only
    code = comment_out_text_only(code, rid)
    
    # 4. Fix comment wrapping (new, highly robust version)
    code = fix_wrapped_comments(code)
    
    # 5. Fix pure virtual destructors
    code = fix_pure_virtual_destructors(code)
    
    # 6. Apply targeted rule patches
    code = apply_rule_patches(rid, code)
    
    # 7. Inject headers
    if not is_comment_only(code):
        code = inject_missing_headers(code)
        
    r['bad'] = code
    r['good'] = code
    
    # 8. Compile check
    if is_comment_only(code):
        r['compiles'] = True
        print(f"[{i+1}/{len(std_autosar_extracted.RULES)}] {rid}: OK (comment only)")
    else:
        compile_code = code
        if 'int main' not in code:
            compile_code = code + "\n\nint main() {\n    return 0;\n}\n"
            
        print(f"[{i+1}/{len(std_autosar_extracted.RULES)}] Compile checking {rid}...", end='', flush=True)
        time.sleep(0.45)
        ok, err = compile_one_cpp14(compile_code)
        
        if ok:
            r['compiles'] = True
            print(" OK")
        else:
            r['compiles'] = False
            print(f" FAIL | {err[:80]}")
            
    cleaned_rules.append(r)

# Write updated rules back
with open('std_autosar_extracted.py', 'w', encoding='utf-8') as f:
    f.write("# -*- coding: utf-8 -*-\n")
    f.write('"""Auto-generated AUTOSAR C++14 rules extracted from PDF."""\n\n')
    f.write("RULES = [\n")
    for r in cleaned_rules:
        f.write("    {\n")
        f.write(f"        'id': {repr(r['id'])},\n")
        f.write(f"        'cat': {repr(r['cat'])},\n")
        f.write(f"        'compiles': {repr(r['compiles'])},\n")
        f.write(f"        'title': {repr(r['title'])},\n")
        f.write(f"        'title_en': {repr(r['title_en'])},\n")
        f.write(f"        'bad': {repr(r['bad'])},\n")
        f.write(f"        'good': {repr(r['good'])},\n")
        f.write(f"        'why': {repr(r['why'])},\n")
        f.write(f"        'why_en': {repr(r['why_en'])},\n")
        f.write("    },\n")
    f.write("]\n")

print("Done! Updated std_autosar_extracted.py")
