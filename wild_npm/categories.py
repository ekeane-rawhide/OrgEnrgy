"""
PRE-REGISTERED category list, written before any category besides
http_client has been crawled or scored. Selection criterion: functionally
interchangeable libraries occupying the same "exclusive dependency slot"
(a dependent package picks ~one), chosen from public JS-ecosystem
knowledge, not from crawl results. No category is added or dropped after
seeing its numbers.
"""

CATEGORIES = {
    "http_client": [
        "axios", "node-fetch", "got", "superagent", "request",
        "cross-fetch", "ky", "undici", "isomorphic-fetch", "needle",
    ],
    "test_runner": [
        "jest", "mocha", "ava", "tape", "jasmine", "vitest", "uvu", "tap",
    ],
    "date_library": [
        "moment", "dayjs", "date-fns", "luxon",
    ],
    "state_management": [
        "redux", "mobx", "zustand", "recoil", "jotai", "xstate", "valtio",
    ],
    "bundler": [
        "webpack", "rollup", "parcel", "esbuild", "browserify",
    ],
    "promise_utils": [
        "bluebird", "q", "when", "rsvp", "es6-promise",
    ],
    "logging": [
        "winston", "bunyan", "pino", "log4js", "loglevel",
    ],
    "templating": [
        "handlebars", "ejs", "pug", "mustache", "nunjucks", "consolidate",
    ],
    "validation": [
        "joi", "yup", "ajv", "zod", "superstruct", "validator",
    ],
    "uuid_gen": [
        "uuid", "nanoid", "shortid", "cuid", "ulid",
    ],
    "cli_args": [
        "yargs", "commander", "minimist", "meow", "yargs-parser",
    ],
}

GENERIC_TERMS = [
    "cli", "react", "webpack", "server", "sdk", "framework", "build",
    "test", "utils", "app", "typescript", "vue", "graphql", "docker",
    "auth", "database", "logger", "config", "cron", "parser",
]
