```cpp
static basic_json diff(const basic_json& source, const basic_json& target,
                       const std::string& path = "")
{
    basic_json result(value_t::array);

    if (source == target)
    {
        return result;
    }

    if (source.type() != target.type())
    {
        result.push_back(
        {
            {"op", "replace"}, {"path", path}, {"value", target}
        });
        return result;
    }

    switch (source.type())
    {
        case value_t::array:
        {
            std::size_t i = 0;
            const std::size_t ssize = source.size();
            const std::size_t tsize = target.size();
            const std::size_t common = ssize < tsize ? ssize : tsize;
            while (i < common)
            {
                auto temp_diff = diff(source[i], target[i], path + "/" + std::to_string(i));
                result.insert(result.end(), temp_diff.begin(), temp_diff.end());
                ++i;
            }

            std::size_t k = ssize;
            while (k > common)
            {
                --k;
                result.push_back(object(
                {
                    {"op", "remove"},
                    {"path", path + "/" + std::to_string(k)}
                }));
            }

            for (; i < tsize; ++i)
            {
                result.push_back(object(
                {
                    {"op", "add"},
                    {"path", path + "/" + std::to_string(i)},
                    {"value", target[i]}
                }));
            }
            break;
        }

        case value_t::object:
        {
            for (auto it = source.cbegin(); it != source.cend(); ++it)
            {
                const auto key = json_pointer::escape(it.key());
                const auto other = target.find(it.key());
                if (other != target.cend())
                {
                    auto temp_diff = diff(it.value(), other.value(), path + "/" + key);
                    result.insert(result.end(), temp_diff.begin(), temp_diff.end());
                }
                else
                {
                    result.push_back(object(
                    {
                        {"op", "remove"}, {"path", path + "/" + key}
                    }));
                }
            }

            for (auto it = target.cbegin(); it != target.cend(); ++it)
            {
                if (source.find(it.key()) == source.cend())
                {
                    result.push_back(object(
                    {
                        {"op", "add"},
                        {"path", path + "/" + json_pointer::escape(it.key())},
                        {"value", it.value()}
                    }));
                }
            }
            break;
        }

        default:
        {
            result.push_back(object(
            {
                {"op", "replace"}, {"path", path}, {"value", target}
            }));
            break;
        }
    }

    return result;
}
```
