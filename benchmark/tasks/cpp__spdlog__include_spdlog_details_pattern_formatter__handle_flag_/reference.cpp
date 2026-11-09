    void handle_flag_(char flag, details::padding_info padding)
    {
        switch (flag)
        {

        case ('+'): // default formatter
            formatters_.push_back(details::make_unique<details::full_formatter>(padding));
            break;

        case 'n': // logger name
            formatters_.push_back(details::make_unique<details::name_formatter>(padding));
            break;

        case 'l': // level
            formatters_.push_back(details::make_unique<details::level_formatter>(padding));
            break;

        case 'L': // short level
            formatters_.push_back(details::make_unique<details::short_level_formatter>(padding));
            break;

        case ('t'): // thread id
            formatters_.push_back(details::make_unique<details::t_formatter>(padding));
            break;

        case ('v'): // the message text
            formatters_.push_back(details::make_unique<details::v_formatter>(padding));
            break;

        case ('a'): // weekday
            formatters_.push_back(details::make_unique<details::a_formatter>(padding));
            break;

        case ('A'): // short weekday
            formatters_.push_back(details::make_unique<details::A_formatter>(padding));
            break;

        case ('b'):
        case ('h'): // month
            formatters_.push_back(details::make_unique<details::b_formatter>(padding));
            break;

        case ('B'): // short month
            formatters_.push_back(details::make_unique<details::B_formatter>(padding));
            break;

        case ('c'): // datetime
            formatters_.push_back(details::make_unique<details::c_formatter>(padding));
            break;

        case ('C'): // year 2 digits
            formatters_.push_back(details::make_unique<details::C_formatter>(padding));
            break;

        case ('Y'): // year 4 digits
            formatters_.push_back(details::make_unique<details::Y_formatter>(padding));
            break;

        case ('D'):
        case ('x'): // datetime MM/DD/YY
            formatters_.push_back(details::make_unique<details::D_formatter>(padding));
            break;

        case ('m'): // month 1-12
            formatters_.push_back(details::make_unique<details::m_formatter>(padding));
            break;

        case ('d'): // day of month 1-31
            formatters_.push_back(details::make_unique<details::d_formatter>(padding));
            break;

        case ('H'): // hours 24
            formatters_.push_back(details::make_unique<details::H_formatter>(padding));
            break;

        case ('I'): // hours 12
            formatters_.push_back(details::make_unique<details::I_formatter>(padding));
            break;

        case ('M'): // minutes
            formatters_.push_back(details::make_unique<details::M_formatter>(padding));
            break;

        case ('S'): // seconds
            formatters_.push_back(details::make_unique<details::S_formatter>(padding));
            break;

        case ('e'): // milliseconds
            formatters_.push_back(details::make_unique<details::e_formatter>(padding));
            break;

        case ('f'): // microseconds
            formatters_.push_back(details::make_unique<details::f_formatter>(padding));
            break;

        case ('F'): // nanoseconds
            formatters_.push_back(details::make_unique<details::F_formatter>(padding));
            break;

        case ('E'): // seconds since epoch
            formatters_.push_back(details::make_unique<details::E_formatter>(padding));
            break;

        case ('p'): // am/pm
            formatters_.push_back(details::make_unique<details::p_formatter>(padding));
            break;

        case ('r'): // 12 hour clock 02:55:02 pm
            formatters_.push_back(details::make_unique<details::r_formatter>(padding));
            break;

        case ('R'): // 24-hour HH:MM time
            formatters_.push_back(details::make_unique<details::R_formatter>(padding));
            break;

        case ('T'):
        case ('X'): // ISO 8601 time format (HH:MM:SS)
            formatters_.push_back(details::make_unique<details::T_formatter>(padding));
            break;

        case ('z'): // timezone
            formatters_.push_back(details::make_unique<details::z_formatter>(padding));
            break;

        case ('P'): // pid
            formatters_.push_back(details::make_unique<details::pid_formatter>(padding));
            break;

#ifdef SPDLOG_ENABLE_MESSAGE_COUNTER
        case ('i'):
            formatters_.push_back(details::make_unique<details::i_formatter>(padding));
            break;
#endif
        case ('^'): // color range start
            formatters_.push_back(details::make_unique<details::color_start_formatter>(padding));
            break;

        case ('$'): // color range end
            formatters_.push_back(details::make_unique<details::color_stop_formatter>(padding));
            break;

        case ('@'): // source location (filename:filenumber)
            formatters_.push_back(details::make_unique<details::source_location_formatter>(padding));
            break;

        case ('s'): // source filename
            formatters_.push_back(details::make_unique<details::source_filename_formatter>(padding));
            break;

        case ('#'): // source line number
            formatters_.push_back(details::make_unique<details::source_linenum_formatter>(padding));
            break;

        case ('!'): // source funcname
            formatters_.push_back(details::make_unique<details::source_funcname_formatter>(padding));
            break;

        case ('%'): // % char
            formatters_.push_back(details::make_unique<details::ch_formatter>('%'));
            break;

        default: // Unknown flag appears as is
            auto unknown_flag = details::make_unique<details::aggregate_formatter>();
            unknown_flag->add_ch('%');
            unknown_flag->add_ch(flag);
            formatters_.push_back((std::move(unknown_flag)));
            break;
        }
    }
