```cpp
void handle_flag_(char flag, details::padding_info padding)
{
    switch (flag)
    {
    case '+':
        formatters_.push_back(details::make_unique<details::full_formatter>(padding));
        break;
    case 'n':
        formatters_.push_back(details::make_unique<details::name_formatter>(padding));
        break;
    case 'l':
        formatters_.push_back(details::make_unique<details::level_formatter>(padding));
        break;
    case 'L':
        formatters_.push_back(details::make_unique<details::short_level_formatter>(padding));
        break;
    case 't':
        formatters_.push_back(details::make_unique<details::t_formatter>(padding));
        break;
    case 'v':
        formatters_.push_back(details::make_unique<details::v_formatter>(padding));
        break;
    case 'a':
        formatters_.push_back(details::make_unique<details::a_formatter>(padding));
        break;
    case 'A':
        formatters_.push_back(details::make_unique<details::A_formatter>(padding));
        break;
    case 'b':
    case 'h':
        formatters_.push_back(details::make_unique<details::b_formatter>(padding));
        break;
    case 'B':
        formatters_.push_back(details::make_unique<details::B_formatter>(padding));
        break;
    case 'c':
        formatters_.push_back(details::make_unique<details::c_formatter>(padding));
        break;
    case 'C':
        formatters_.push_back(details::make_unique<details::C_formatter>(padding));
        break;
    case 'Y':
        formatters_.push_back(details::make_unique<details::Y_formatter>(padding));
        break;
    case 'D':
    case 'x':
        formatters_.push_back(details::make_unique<details::D_formatter>(padding));
        break;
    case 'm':
        formatters_.push_back(details::make_unique<details::m_formatter>(padding));
        break;
    case 'd':
        formatters_.push_back(details::make_unique<details::d_formatter>(padding));
        break;
    case 'H':
        formatters_.push_back(details::make_unique<details::H_formatter>(padding));
        break;
    case 'I':
        formatters_.push_back(details::make_unique<details::I_formatter>(padding));
        break;
    case 'M':
        formatters_.push_back(details::make_unique<details::M_formatter>(padding));
        break;
    case 'S':
        formatters_.push_back(details::make_unique<details::S_formatter>(padding));
        break;
    case 'e':
        formatters_.push_back(details::make_unique<details::e_formatter>(padding));
        break;
    case 'f':
        formatters_.push_back(details::make_unique<details::f_formatter>(padding));
        break;
    case 'F':
        formatters_.push_back(details::make_unique<details::F_formatter>(padding));
        break;
    case 'E':
        formatters_.push_back(details::make_unique<details::E_formatter>(padding));
        break;
    case 'p':
        formatters_.push_back(details::make_unique<details::p_formatter>(padding));
        break;
    case 'r':
        formatters_.push_back(details::make_unique<details::r_formatter>(padding));
        break;
    case 'R':
        formatters_.push_back(details::make_unique<details::R_formatter>(padding));
        break;
    case 'T':
    case 'X':
        formatters_.push_back(details::make_unique<details::T_formatter>(padding));
        break;
    case 'z':
        formatters_.push_back(details::make_unique<details::z_formatter>(padding));
        break;
    case 'P':
        formatters_.push_back(details::make_unique<details::pid_formatter>(padding));
        break;
    case 'i':
        formatters_.push_back(details::make_unique<details::i_formatter>(padding));
        break;
    case '^':
        formatters_.push_back(details::make_unique<details::color_start_formatter>(padding));
        break;
    case '$':
        formatters_.push_back(details::make_unique<details::color_stop_formatter>(padding));
        break;
    case '@':
        formatters_.push_back(details::make_unique<details::source_location_formatter>(padding));
        break;
    case 's':
        formatters_.push_back(details::make_unique<details::source_filename_formatter>(padding));
        break;
    case '#':
        formatters_.push_back(details::make_unique<details::source_linenum_formatter>(padding));
        break;
    case '!':
        formatters_.push_back(details::make_unique<details::source_funcname_formatter>(padding));
        break;
    case '%':
        formatters_.push_back(details::make_unique<details::ch_formatter>('%'));
        break;
    default:
    {
        auto unknown_flag = details::make_unique<details::aggregate_formatter>();
        unknown_flag->add_ch('%');
        unknown_flag->add_ch(flag);
        formatters_.push_back(std::move(unknown_flag));
        break;
    }
    }
}
```
