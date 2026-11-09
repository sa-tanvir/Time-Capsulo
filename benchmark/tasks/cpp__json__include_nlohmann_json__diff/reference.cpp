static basic_json diff(const basic_json& source, const basic_json& target,
                       const std::string& path = "")
{
    // the patch
    basic_json result(value_t::array);

    // if the values are the same, return empty patch
    if (source == target)
    {
        return result;
    }

    if (source.type() != target.type())
    {
        // different types: replace value
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
            // first pass: traverse common elements
            std::size_t i = 0;
            while (i < source.size() and i < target.size())
            {
                // recursive call to compare array values at index i
                auto temp_diff = diff(source[i], target[i], path + "/" + std::to_string(i));
                result.insert(result.end(), temp_diff.begin(), temp_diff.end());
                ++i;
            }

            // i now reached the end of at least one array
            // in a second pass, traverse the remaining elements

            // remove my remaining elements
            const auto end_index = static_cast<difference_type>(result.size());
            while (i < source.size())
            {
                // add operations in reverse order to avoid invalid
                // indices
                result.insert(result.begin() + end_index, object(
                {
                    {"op", "remove"},
                    {"path", path + "/" + std::to_string(i)}
                }));
                ++i;
            }

            // add other remaining elements
            while (i < target.size())
            {
                result.push_back(
                {
                    {"op", "add"},
                    {"path", path + "/" + std::to_string(i)},
                    {"value", target[i]}
                });
                ++i;
            }

            break;
        }

        case value_t::object:
        {
            // first pass: traverse this object's elements
            for (auto it = source.cbegin(); it != source.cend(); ++it)
            {
                // escape the key name to be used in a JSON patch
                const auto key = json_pointer::escape(it.key());

                if (target.find(it.key()) != target.end())
                {
                    // recursive call to compare object values at key it
                    auto temp_diff = diff(it.value(), target[it.key()], path + "/" + key);
                    result.insert(result.end(), temp_diff.begin(), temp_diff.end());
                }
                else
                {
                    // found a key that is not in o -> remove it
                    result.push_back(object(
                    {
                        {"op", "remove"}, {"path", path + "/" + key}
                    }));
                }
            }

            // second pass: traverse other object's elements
            for (auto it = target.cbegin(); it != target.cend(); ++it)
            {
                if (source.find(it.key()) == source.end())
                {
                    // found a key that is not in this -> add it
                    const auto key = json_pointer::escape(it.key());
                    result.push_back(
                    {
                        {"op", "add"}, {"path", path + "/" + key},
                        {"value", it.value()}
                    });
                }
            }

            break;
        }

        default:
        {
            // both primitive type: replace value
            result.push_back(
            {
                {"op", "replace"}, {"path", path}, {"value", target}
            });
            break;
        }
    }

    return result;
}
