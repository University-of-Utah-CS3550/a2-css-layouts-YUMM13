function say_hi(elt) {
    console.log("Welcome to", elt.innerText);
}

say_hi(document.querySelector("span"));

function make_table_sortable(table) {
    // make sure table is sortable
    if (!table.classList.contains("sortable")) { return; }

    // get sortable headers
    let headers = table.querySelectorAll(".sort-column");
    console.log(headers);
    headers.forEach(header => {
        // add click handler to header
        header.addEventListener("click", (event) => {
            // get sorted state using class name
            let state = header.classList;
    
            if (state.contains("sort-column")) {
                // make sort-asc
                header.classList.replace("sort-column" ,"sort-asc");
                let body = table.querySelector("tbody");
                console.log(event.target.cellIndex);
                let rows = Array.from(body.querySelectorAll("tr")).sort((a, b) => {
                    let aGrade = parseFloat(a.querySelector(".tableNum").textContent);
                    let bGrade = parseFloat(b.querySelector(".tableNum").textContent);
                    return aGrade - bGrade;
                });
    
                rows.forEach(row => body.appendChild(row));
            }            
            else if (state.contains("sort-asc")) {
                // make sort-desc
                header.classList.replace("sort-asc" ,"sort-desc");
                let body = table.querySelector("tbody");
                let rows = Array.from(body.querySelectorAll("tr")).sort((a, b) => {
                    let aGrade = parseFloat(a.querySelector(".tableNum").textContent);
                    let bGrade = parseFloat(b.querySelector(".tableNum").textContent);
                    return bGrade - aGrade;
                });
        
                rows.forEach(row => body.appendChild(row));
            }
            else {
                // restore original order
                header.classList.replace("sort-desc" ,"sort-column");
                let body = table.querySelector("tbody");
                let rows = Array.from(body.querySelectorAll("tr")).sort((a, b) => {
                    let aIndex = a.getAttribute("data-index");
                    let bIndex = b.getAttribute("data-index");
                    return aIndex - bIndex;
                });
        
                rows.forEach(row => body.appendChild(row));
            }
        })
    });
}

const tables = document.querySelectorAll('table.sortable');
tables.forEach(element => {
    make_table_sortable(element);
});