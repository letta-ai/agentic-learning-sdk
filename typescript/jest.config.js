module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],

  // Test discovery - look in unit/ and integration/ directories
  // Note: Exclude .mts files (those use tsx runner, not Jest)
  testMatch: ['**/tests/unit/**/*.test.ts', '**/tests/integration/**/*.test.ts'],

  // Ignore shared and setup files
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/tests/shared/',
    '/tests/unit/setup.ts',
    '/tests/integration/setup.ts',
  ],

  moduleFileExtensions: ['ts', 'js', 'json', 'mjs'],

  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
  ],

  transform: {
    '^.+\\.ts$': ['ts-jest', {
      tsconfig: {
        esModuleInterop: true,
      },
    }],
    '^.+\\.mjs$': 'babel-jest',
  },

  // Transform ESM modules from node_modules
  transformIgnorePatterns: [
    'node_modules/(?!@anthropic-ai/claude-agent-sdk)',
  ],

  // Test timeout for async operations with cloud APIs
  testTimeout: 60000,

  // Display test names during execution
  verbose: true,
};
