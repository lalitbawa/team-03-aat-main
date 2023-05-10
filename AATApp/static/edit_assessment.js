all_options = {};

function processResponse() {
    let data = JSON.parse(this.response);
    for (let i = 0; i < data.length; i++) {
        addOption(data[i]['question'], data[i]['id']);
    }

    $( function() {
        $( "#sortable-list" ).sortable();
        let existing_questions = $(`#sortable-list`).children();
        console.log(existing_questions);
        for (let i = 0; i < existing_questions.length; i++) {
            question_id = existing_questions[String(i)].getAttribute('class').split(' ')[1];
            $(`#select-question option[value=${question_id}]`).remove();
        }
    });
}

let xhttp = new XMLHttpRequest();
xhttp.addEventListener('load', processResponse);
xhttp.open('GET',`/get_all_questions`);
xhttp.send();

function addOption(optText, optValue) {
    $('#select-question').append(`<option value="${optValue}">${optText}</option>`);
    all_options[optValue] = optText;
}

$( function() {
    $(".remove-item").click(function() {
        let question_id = $(this).parent().attr('class').split(' ')[1]
        $('#select-question').append(`<option value="${question_id}">${all_options[question_id]}</option>`);
        $(this).parent().remove();
    });    
})


$( function() {
    $("#add-question").click(function(){
        if($(`#sortable-list`).children().length < 10) {
            question_content = $( "#select-question option:selected" ).text();
            question_id = $( "#select-question").val();
            var new_li = $(`<li class=\"list-group-item ${question_id}\"></li>`).text(question_content);
            $("#sortable-list").append(new_li);
            new_li.append($( `<input type=\"hidden\" name=\"question\"></input>`).val(question_id));
            new_li.append($(`<span class='float-end remove-item' style='cursor: pointer;'></span>`).text('X')); 
            $(`#select-question option[value=${question_id}]`).remove();

            $(".remove-item").click(function() {
                let question_id = $(this).parent().attr('class').split(' ')[1]
                $('#select-question').append(`<option value="${question_id}">${all_options[question_id]}</option>`);
                $(this).parent().remove();
            });
        }
        if ($(`#sortable-list`).children().length == 10 || (document.getElementById('select-question').options).length == 0)
        {
            $('#add-question-div').hide();
        }
    });
});