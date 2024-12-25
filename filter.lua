function Div(el)
    if #el.classes > 0 then
        local some_word = el.classes[1]
	el.classes = {}
        el.attributes["box"] = some_word
        local capitalized_word = string.upper(some_word)
        local capitalized_intro = pandoc.Para({pandoc.Str(capitalized_word .. ":")})
        table.insert(el.content, 1, capitalized_intro)
    end
    return el
end
