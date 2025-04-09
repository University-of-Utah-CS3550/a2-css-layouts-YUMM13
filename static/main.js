function say_hi(elt) {
    console.log("Welcome to", elt.innerText);
}

say_hi(document.querySelector("span"));

function make_table_sortable(table) {
    // make sure table is sortable
    if (!table.classList.contains("sortable")) { return; }

    // get last header in table
    let headers = table.querySelectorAll("thead th")
    let header = headers[headers.length - 1];

    // add click handler to header
    header.addEventListener("click", () => {
        console.log("Clicked!");
        // get sorted state using class name
        let state = header.classList;

        if (state.contains("sortable")) {
            // make sort-asc
            header.classList.replace("sortable" ,"sort-asc");
            let body = table.querySelector("tbody");
            let rows = Array.from(body.querySelectorAll("tr")).sort((a, b) => {
                let aGrade = parseFloat(a.querySelector(".tableNum").textContent);
                let bGrade = parseFloat(b.querySelector(".tableNum").textContent);
                return aGrade - bGrade;
            });

            rows.forEach(row => body.appendChild(row));
        }            
        else if (state.contains("sort-desc")) {
            // make sort-asc
            header.classList.replace("sort-desc" ,"sort-asc");
            let body = table.querySelector("tbody");
            let rows = Array.from(body.querySelectorAll("tr")).sort((a, b) => {
                let aGrade = parseFloat(a.querySelector(".tableNum").textContent);
                let bGrade = parseFloat(b.querySelector(".tableNum").textContent);
                return aGrade - bGrade;
            });

            rows.forEach(row => body.appendChild(row));
        }
        else {
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
    })
}

const table = document.querySelector('table.sortable');
console.log(table);
make_table_sortable(table);