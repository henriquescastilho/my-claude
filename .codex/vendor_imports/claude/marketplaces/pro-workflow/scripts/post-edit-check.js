#!/usr/bin/env node
/**
 * Post-Edit Check
 *
 * Runs after code edits to catch common issues.
 * Supports the self-correction loop by surfacing potential mistakes.
 */

const fs = require('fs');

function log(msg) {
  console.error(msg);
}

async function main() {
  let data = '';

  process.stdin.on('data', chunk => {
    data += chunk;
  });

  process.stdin.on('end', () => {
    try {
      const input = JSON.parse(data);
      const filePath = input.tool_input?.file_path;

      if (!filePath || !fs.existsSync(filePath)) {
        console.log(data);
        return;
      }

      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      const issues = [];

      lines.forEach((line, idx) => {
        const lineNum = idx + 1;

        // Check for console.log (JS/TS)
        if (/console\.(log|debug|info)\(/.test(line) && !/\/\/.*console/.test(line)) {
          issues.push(`${lineNum}: console.log found`);
        }

        // Check for print statements (Python)
        if (/\bprint\s*\(/.test(line) && !/^#/.test(line.trim()) && filePath.endsWith('.py')) {
          issues.push(`${lineNum}: print() found`);
        }

        // Check for TODO/FIXME
        if (/\b(TODO|FIXME|XXX|HACK)\b/i.test(line)) {
          issues.push(`${lineNum}: ${line.match(/\b(TODO|FIXME|XXX|HACK)\b/i)[0]} found`);
        }

        // Check for hardcoded secrets patterns
        if (/(['"])?(api[_-]?key|secret|password|token)(['"])?[\s]*[:=][\s]*(['"])[^'"]{8,}/i.test(line)) {
          issues.push(`${lineNum}: Possible hardcoded secret`);
        }
      });

      if (issues.length > 0) {
        log(`[ProWorkflow] Issues in ${filePath}:`);
        issues.slice(0, 5).forEach(issue => log(`  ${issue}`));
        if (issues.length > 5) {
          log(`  ... and ${issues.length - 5} more`);
        }
        log('[ProWorkflow] Consider: [LEARN] to remember patterns');
      }

      console.log(data);
    } catch (err) {
      console.log(data);
    }
  });
}

main().catch(err => {
  console.error('[ProWorkflow] Error:', err.message);
  process.exit(0);
});
