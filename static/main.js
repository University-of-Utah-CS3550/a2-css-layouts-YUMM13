function say_hi(elt) {
    console.log("Welcome to", elt.innerText);
}

say_hi(document.querySelector("span"));

function make_table_sortable(table) {
    // make sure table is sortable
    if (!table.classList.contains("sortable")) { return; }

    // get sortable headers
    let headers = table.querySelectorAll(".sort-column");
    // console.log(headers);
    headers.forEach(header => {
        // add click handler to header
        header.addEventListener("click", (event) => {
            // get sorted state using class name
            let state = header.classList;
            let colIndex = event.target.cellIndex;
    
            if (state.contains("sort-column")) {
                // make sort-asc
                remove_other_sorts(table);
                header.classList.replace("sort-column" ,"sort-asc");
                let body = table.querySelector("tbody");
                let rows = Array.from(body.querySelectorAll("tr")).sort((a, b) => {
                    let aGrade = parseFloat(a.cells[colIndex].getAttribute("data-value"));
                    let bGrade = parseFloat(b.cells[colIndex].getAttribute("data-value"));
                    return aGrade - bGrade;
                });
    
                rows.forEach(row => body.appendChild(row));
            }            
            else if (state.contains("sort-asc")) {
                // make sort-desc
                remove_other_sorts(table);
                header.classList.replace("sort-column" ,"sort-desc");
                let body = table.querySelector("tbody");
                let rows = Array.from(body.querySelectorAll("tr")).sort((a, b) => {
                    let aGrade = parseFloat(a.cells[colIndex].getAttribute("data-value"));
                    let bGrade = parseFloat(b.cells[colIndex].getAttribute("data-value"));
                    return bGrade - aGrade;
                });
        
                rows.forEach(row => body.appendChild(row));
            }
            else {
                // restore original order
                remove_other_sorts(table);
                // header.classList.replace("sort-" ,"sort-column");
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

function remove_other_sorts(table) {
    // get other headers with sort-asc or sort-desc
    let otherCols = table.querySelectorAll(".sort-asc,.sort-desc");
    console.log(otherCols);
    otherCols.forEach(col => {
        if (col.classList.contains("sort-asc")) { col.classList.replace("sort-asc", "sort-column"); }
        if (col.classList.contains("sort-desc")) { col.classList.replace("sort-desc", "sort-column"); }
    });
}

const tables = document.querySelectorAll('table.sortable');
tables.forEach(element => {
    make_table_sortable(element);
});

function make_form_async(form) {
    form.addEventListener("submit", async (event) => {
        console.log("Running");
        // remove default action
        event.preventDefault();

        // construct form data instance
        const formData = new FormData(form);

        // grab the csrf token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // try to send the form data
        try {
            const response = await fetch(form.action, {
                headers: {
                'X-CSRFToken': csrfToken,
                },
                method: "POST",
                body: formData,
            });
            if (response.ok) {
                let success = document.createElement("p");
                success.innerText = "Upload Succeeded!";
                form.appendChild(success);
            }
            else {
            let failed = document.createElement("p");
            failed.innerText = "Upload Failed!";
            form.appendChild(failed);
            }
        } catch (e) {
            console.log("An error ocurred while submitting your work: ", e);
        }
    });
}

const form = document.querySelector('.assignment-form');
if (form){ make_form_async(form); }

function make_grade_hypothesized(table) {
    // create hypothesize button
    let hypButton = document.createElement('button');
    hypButton.innerText = "Hypothesize"
    table.parentNode.insertBefore(hypButton, table);

    // create click listener for button
    hypButton.addEventListener('click', () => {
        let classes = table.classList;

        if (!classes.contains("hypothesized")) {
            // change state
            classes.add("hypothesized");
            hypButton.innerText = "Actual Grades";

            // swap grades with inputs
            let grades = table.querySelectorAll(".tableNum");
            console.log(grades);
            grades.forEach(g => {
                if (g.innerText === "Not Due" || g.innerText === "Not Graded") {
                    let input = document.createElement("input");
                    input.classList.add("tableNum");
                    g.dataset.status = g.innerHTML;
                    g.innerHTML = "";
                    g.appendChild(input);
                }
            })
        }
        else {
            // change state
            classes.remove("hypothesized");
            hypButton.innerText = "Hypothesized";

            // swap inputs with grades
            let inputs = table.querySelectorAll(".tableNum");
            console.log(inputs);
            inputs.forEach(i => {
                g.style.display = "";
                i.remove();
            })
        }
    });
}

const table = document.querySelector(".hypoth");
if (table) { make_grade_hypothesized(table); }