
function search()
{
    var category_input = document.getElementById("search_input")
    var categories = document.getElementsByName("category_cell")
    var search_category = category_input.value.toLowerCase();

    var name_input = document.getElementById("name_input")
    var names = document.getElementsByName("name_cell")
    var search_name = name_input.value.toLowerCase()

    for(var i = 0; i < names.length; i++) //i += 1  for i in range(len(elements))
    {
        var name = names[i].innerHTML.toLowerCase()
        var category = categories[i].innerHTML.toLowerCase()
        if(name.includes(search_name) && category.includes(search_category))
        {
            names[i].parentNode.style.display = ""
        }
        else
        {
            names[i].parentNode.style.display = "none"
        }
    }
}

function search_history()
{
    var category_input = document.getElementById("search_input")
    var categories = document.getElementsByName("category_cell")
    var search_category = category_input.value.toLowerCase();

    var name_input = document.getElementById("name_input")
    var names = document.getElementsByName("name_cell")
    var search_name = name_input.value.toLowerCase()

    for(var i = 0; i < names.length; i++)
    {
        var name = names[i].innerHTML.toLowerCase()
        var category = categories[i].innerHTML.toLowerCase()
        if(name.includes(search_name) && category.includes(search_category))
        {
            names[i].parentNode.style.display = ""
        }
        else
        {
            names[i].parentNode.style.display = "none"
        }
    }
}