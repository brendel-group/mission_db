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
      '^.+\\.(ts|tsx)$': 'ts-jest'
    },
    collectCoverageFrom: [
      'app/**/*.{ts,tsx}',
      '!app/**/*.d.ts'
    ]
  };