import js from '@eslint/js';
import svelte from 'eslint-plugin-svelte';
import svelteParser from 'svelte-eslint-parser';
import prettier from 'eslint-config-prettier';
import globals from 'globals';

export default [
  js.configs.recommended,
  ...svelte.configs['flat/recommended'],
  prettier,
  {
    files: ['**/*.{js,svelte}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node
      }
    },
    rules: {
      'no-unused-vars': [
        'warn',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_'
        }
      ],
      'no-console': 'off', // Allow console statements for development
      'no-debugger': 'warn',
      'no-useless-catch': 'off',
      'no-dupe-keys': 'error'
    }
  },
  {
    files: ['**/*.svelte'],
    languageOptions: {
      parser: svelteParser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module'
      }
    },
    rules: {
      'svelte/require-each-key': 'off', // Disable each key requirement for development
      'svelte/no-at-html-tags': 'off' // Disable @html warnings since we use DOMPurify for sanitization
    }
  },
  {
    files: ['tailwind.config.js', 'vite.config.js', 'svelte.config.js', 'postcss.config.js'],
    languageOptions: {
      globals: {
        ...globals.node
      }
    }
  },
  {
    ignores: ['dist/', 'build/', 'node_modules/', '.svelte-kit/', '**/*.d.ts']
  }
];
