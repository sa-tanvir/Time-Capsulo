# Context for the function to implement

- **Language:** javascript
- **File:** `src/lib/create/from-string.js`

## Imports / includes available in this file

```
import { configFromStringAndFormat } from './from-string-and-format';
import { createUTCDate } from './date-from-array';
import { configFromArray } from './from-array';
import { hooks } from '../utils/hooks';
import { deprecate } from '../utils/deprecate';
import getParsingFlags from './parsing-flags';
import {defaultLocaleMonthsShort} from '../units/month';
import {defaultLocaleWeekdaysShort} from '../units/day-of-week';
```

## Other functions defined in the same file (signatures only; you may call them)

```
(anonymous) ( config )
calculateOffset ( obsOffset , militaryOffset , numOffset )
checkWeekday ( weekdayStr , parsedInput , config )
configFromRFC2822 ( config )
configFromString ( config )
extractFromRFC2822Strings ( yearStr , monthStr , dayStr , hourStr , minuteStr , secondStr )
preprocessRFC2822 ( s )
untruncateYear ( yearStr )
```

## Variables declared at the same scope level (you may use them)

```
var extendedIsoRegex = /^\s*((?:[+-]\d{6}|\d{4})-(?:\d\d-\d\d|W\d\d-\d|W\d\d|\d\d\d|\d\d))(?:(T| )(\d\d(?::\d\d(?::\d\d(?:[.,]\d+)?)?)?)([\+\-]\d\d(?::?\d\d)?|\s*Z)?)?$/;
var basicIsoRegex = /^\s*((?:[+-]\d{6}|\d{4})(?:\d\d\d\d|W\d\d\d|W\d\d|\d\d\d|\d\d))(?:(T| )(\d\d(?:\d\d(?:\d\d(?:[.,]\d+)?)?)?)([\+\-]\d\d(?::?\d\d)?|\s*Z)?)?$/;
var tzRegex = /Z|[+-]\d\d(?::?\d\d)?/;
var isoDates = [
    ['YYYYYY-MM-DD', /[+-]\d{6}-\d\d-\d\d/],
    ['YYYY-MM-DD', /\d{4}-\d\d-\d\d/],
    ['GGGG-[W]WW-E', /\d{4}-W\d\d-\d/],
    ['GGGG-[W]WW', /\d{4}-W\d\d/, false],
    ['YYYY-DDD', /\d{4}-\d{3}/],
    ['YYYY-MM', /\d{4}-\d\d/, false],
    ['YYYYYYMMDD', /[+-]\d{10}/],
    ['YYYYMMDD', /\d{8}/],
    // YYYYMM is NOT allowed by the standard
    ['GGGG[W]WWE', /\d{4}W\d{3}/],
    ['GGGG[W]WW', /\d{4}W\d{2}/, false],
    ['YYYYDDD', /\d{7}/]
];
var isoTimes = [
    ['HH:mm:ss.SSSS', /\d\d:\d\d:\d\d\.\d+/],
    ['HH:mm:ss,SSSS', /\d\d:\d\d:\d\d,\d+/],
    ['HH:mm:ss', /\d\d:\d\d:\d\d/],
    ['HH:mm', /\d\d:\d\d/],
    ['HHmmss.SSSS', /\d\d\d\d\d\d\.\d+/],
    ['HHmmss,SSSS', /\d\d\d\d\d\d,\d+/],
    ['HHmmss', /\d\d\d\d\d\d/],
    ['HHmm', /\d\d\d\d/],
    ['HH', /\d\d/]
];
var aspNetJsonRegex = /^\/?Date\((\-?\d+)/i;
var rfc2822 = /^(?:(Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s)?(\d{1,2})\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s(\d{2,4})\s(\d\d):(\d\d)(?::(\d\d))?\s(?:(UT|GMT|[ECMP][SD]T)|([Zz])|([+-]\d{4}))$/;
var obsOffsets = {
    UT: 0,
    GMT: 0,
    EDT: -4 * 60,
    EST: -5 * 60,
    CDT: -5 * 60,
    CST: -6 * 60,
    MDT: -6 * 60,
    MST: -7 * 60,
    PDT: -7 * 60,
    PST: -8 * 60
};
```

## The config object and the helpers used

`config` is moment's internal creation config (built by `moment(input, …)` / `moment.utc(…)`):
`config._i` is the input string, `config._f` the format (undefined when called for
`moment(string)`, or `hooks.ISO_8601` when called from format parsing), `config._locale`,
`config._strict`, `config._useUTC`. Validity is recorded in `config._isValid` (`false` = invalid;
when it stays unset, validity is computed later from the parsing flags).

- `getParsingFlags(config)` (imported from `./parsing-flags`): returns the parsing-flags object
  of the config (`config._pf`), creating it with default values on first use. Its boolean `iso`
  flag records that the input looked like ISO 8601.
- `configFromStringAndFormat(config)` (imported from `./from-string-and-format`): parses
  `config._i` according to the moment format string in `config._f` and fills the config
  (date parts, `Date`, flags). Format tokens used here: `YYYY`, `YYYYYY` (6-digit signed year),
  `MM`, `DD`, `DDD` (day of year), `GGGG`/`WW`/`E` (ISO week-year, week, weekday), `HH`, `mm`,
  `ss`, `SSSS` (fraction), `Z` (offset or `Z`), bracketed literals such as `[W]`.
- In the variables above: `extendedIsoRegex` / `basicIsoRegex` recognise a whole ISO string
  (optional leading whitespace); capture group 1 is the date part, group 2 the date/time separator
  (`T` or space), group 3 the time part, group 4 the zone part. `isoDates` and `isoTimes` are
  ordered lists of `[momentFormat, regex]` (dates may have a third element `false` meaning "no time
  allowed with this date form"); `tzRegex` recognises a zone designator.
