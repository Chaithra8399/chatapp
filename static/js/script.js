var scriptElement = document.createElement('script');

// Set the source attribute to the CDN link
scriptElement.src = "https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js";

// Append the script element to the document
document.head.appendChild(scriptElement);
console.log(scriptElement)
{/* <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js" integrity="sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA==" crossorigin="anonymous"></script> */}

var socket = io.connect('http://' + document.domain + ':' + location.port);

var selectuserId;
var counterdata;
var current_user;
// var filterSearchData = {{ filter_search | tojson | safe }};



function chatItemClick(userId) {
    selectuserId=userId;
    console.log(userId);
    // var username= document.getElementById(userId).innerHTML
    var username= document.getElementById('names' + userId).innerHTML
    console.log(username)
    document.getElementById('displayedUsername').innerText = username;
    clearChatMessages()
    loadPreviousMessages()
    mark_msg_seen()


}

function performSearch() {
    var input, filter, chatItems, userNames, i, txtValue;
    input = document.getElementById('search');
    filter = input.value.toUpperCase();
    chatItems = document.querySelectorAll('.chat-item');

    for (i = 0; i < chatItems.length; i++) {
        userNames = chatItems[i].querySelector('.user-name');
        txtValue = userNames.textContent || userNames.innerText;

        // Check if the current chat item's username starts with the filter text
        if (txtValue.toUpperCase().startsWith(filter)) {
            chatItems[i].style.display = '';
        } else {
            chatItems[i].style.display = 'none';
        }
    }
}






socket.on('update_status',function(data){
    console.log(data.user_id,"curernt user -")
    console.log(data.status,"-status that connect")
    console.log(selectuserId,"selected user to show status")
    if (data.user_id==selectuserId){
        document.getElementById('status').innerHTML=data.status
    }
})

socket.on('disconnect',function(data){
    console.log("disconnect from server")
    console.log(data.status,"last seen=")
    
    if (data.user_id==selectuserId){
        document.getElementById('status').innerHTML= "Last_seen" +data.status
    }
    
})

// function filterUsers() {
//     const searchInput = document.getElementById('user-search');
//     const searchValue = searchInput.value.toLowerCase();

//     fetch('/search', {method: 'POST',
//     })
//     .then(response => response.json())
//     .then(data => {
//         const resultsDiv = document.getElementById('search-results');
//         resultsDiv.innerHTML = '';

//         data.users.forEach(user => {
//             const userDiv = document.createElement('div');
//             userDiv.textContent = user;
//             resultsDiv.appendChild(userDiv);
//         });
//     });
// }







// function mark_msg_seen(){
//     fetch(`/mark_message_seen`,{method:'POST'})
//     .then(response => response.json())
//                 .then(data => {
//                         console.log(data,"message seen",data);
//                         document.getElementById(selectuserId).style.display="none"
//                     })
//                     .catch(error=>console.error("error marking message as read",error))

//                 }

// Function to mark messages as seen on the client side
function mark_msg_seen() {
    fetch('/mark_message_seen', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data, "message seen", data);
            // Assuming selectuserId is the ID of the chat element, hide it on success
            if (selectuserId) {
                document.getElementById(selectuserId).style.display = "none";
            }
        })
        .catch(error => console.error("Error marking message as read", error));
}


function clearChatMessages(){
    var chatContainer = document.querySelector('.user-middle');
      chatContainer.innerHTML = '';
}
// function loadPreviousMessages(){
//     if(selectuserId){
//         console.log(selectuserId, "is the useeeeeeeeeeeee")
//         var chatContainer=document.querySelector('.user-middle')
//         if(chatContainer){
//             clearChatMessages()
//             fetch(`/getallmessages/${selectuserId}`) 
//                 .then(response => response.json())  
//                 .then(data => {
//                 data.forEach(message => {
//                 console.log(message,"data message")
//                 appendMessageToChat(message, true);
//             });

//         })
//         .catch(error => console.error('Error fetching messages:', error));
//     }
//     else{
//         console.log("eroooooo")
//     }

//         }

//     }    
    
function loadPreviousMessages() {
    if (selectuserId) {
        var chatContainer=document.getElementById('user-middle')
        if (chatContainer) {
            // Clear the chat container before loading previous messages
            clearChatMessages()

            fetch(`/getallmessages/${selectuserId}`)
                .then(response => response.json())
                .then(data => {
                    console.log(data)
                    console.log("js status",data.status)
                    
                    if(data.status == "online"){
                        document.getElementById('status').innerText=data.status
                    }
                    else{
                        document.getElementById('status').innerText=data.status
                    }

                    
                    data.message_data.forEach(message => {
                        console.log(message,"this is my message")
                        appendMessageToChat(message, true);

                    });


                })

            


                // .catch(error => console.error('Error fetching messages:', error));
        }
        // Add code here to redirect to 'chatpage.html' with the current_user data
        
        console.log("first")
    } else {
        // document.getElementById('message-form').style.display = 'none';
        console.log("sssss")
    }
}
    


 function sendMessage(){
    var content= document.getElementById('message-input').value;
    console.log(content)
    var currentTime = new Date().toISOString();
    console.log(currentTime)
    socket.emit('messagesent',{'selectuserId':selectuserId,'message' : content, 'time': currentTime })

    // Clear the message input field after sending the message
    document.getElementById('message-input').value = '';


 }




 socket.on('message',  function (data) {
    console.log("received message event");
    if (selectuserId != null) {
        appendMessageToChat(data);
    }
    // appendMessageToChat(data);
    console.log(data);
    console.log("selected user",selectuserId)
    console.log("count",counterdata)
    console.log("data sender",data.sender)
    console.log("my session user",current_user)
    if(data.sender!=current_user){
        if(Number(data.sender)!=Number(selectuserId)){
            counterdata[data.sender]+=1
            console.log("unseen message count",counterdata[data.sender])
            document.getElementById(data.sender).innerText=counterdata[data.sender]
            message_count()
            
        }
    }

    
    



    });



// Function to append a new message to the web page
function appendMessageToChat(message) {
    console.log("received messages",message)
    var userMiddleDiv = document.querySelector('.user-middle');
    console.log(user_id)
    var messageDiv = document.createElement('div');

    var messageClass = (message.sender == user_id) ? 'sender-message' : 'receiver-message';

    // Add the determined class to the message div
    messageDiv.className = 'message ' + messageClass;


    // var messageContent = `<p>${message.sender}: ${message.content}</p><small>${message.time}</small>`;
    var messageContent = `<p> ${message.content}</p><small>${formatTime(message.time)}</small>`;


    messageDiv.innerHTML = messageContent;

    userMiddleDiv.appendChild(messageDiv);



}
function formatTime(timeString) {
    const date = new Date(timeString);
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const period = hours >= 12 ? 'pm' : 'am';
    const formattedHours = (hours % 12) || 12;

    const formattedTime = `${formattedHours}:${minutes < 10 ? '0' : ''}${minutes} ${period}`;
    return formattedTime;
}

// function formatTime(timeString) {
//   // Split the time string into hours and minutes
//   const [hours, minutes] = timeString.split(':');

//   // Convert hours to 12-hour format
//   const formattedHours = (hours % 12) || 12;

//   // Determine AM or PM
//   const period = hours < 12 ? 'am' : 'pm';

//   // Format the time as (2:00 pm)
//   const formattedTime = `${formattedHours}:${minutes} ${period}`;

//   return formattedTime;
// }






function message_count(){
    fetch(`/get_unread_count`)
                .then(response => response.json())
                .then(data => {
                    
                    console.log(data,"coreecteddddd");  
                counterdata=data['message_count']
                current_user = data['curr_user']
                console.log(current_user,"this is current user")
                for(key in counterdata){
                    if (counterdata[key]==0){
                        document.getElementById(key).style.display="none"
                    }
                    else{
                        document.getElementById(key).style.display="block"
                    }
                }
                    
                for(userId in data['message_count']){
                    document.getElementById(userId).innerText=data['message_count'][userId];
                }    
                })
                .catch(error => console.error('Error fetching unread count:', error));
        }
document.addEventListener('DOMContentLoaded',function(){
    message_count();
})               


            
