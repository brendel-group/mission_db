module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/jest.setup.cjs'],
    moduleNameMapper: {
      '^~/(.*)$': '<rootDir>/app/$1',
      '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
    },
    testMatch: [
      '<rootDir>/app/**/*.test.{ts,tsx}'
    ],
    transform: {
      '^.+\\.(ts|tsx)$': [
        'ts-jest',
        {
          diagnostics: {
            ignoreCodes: [1343]
          },
          astTransformers: {
            before: [
              {
                path: 'node_modules/ts-jest-mock-import-meta',  // or, alternatively, 'ts-jest-mock-import-meta' directly, without node_modules.
                options: { metaObjectReplacement: { env: {} } } // mock import.meta.env
              }
            ]
          }
        }
      ]
    },
    collectCoverageFrom: [
      'app/**/*.{ts,tsx}',
      '!app/**/*.d.ts'
    ]
  };