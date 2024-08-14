
$(function () {
    var device;
    var To;
    var From;
    log("Requesting Access Token...");
    // Using a relative link to access the Voice Token function
    $.getJSON("/token")
        .then(function (data) {
            log("Got a token.");
            console.log("Token: " + data.token);
            // Setup Twilio.Device
            device = new Twilio.Device(data.token, {
                // Set Opus as our preferred codec. Opus generally performs better, requiring less bandwidth and
                // providing better audio quality in restrained network conditions. Opus will be default in 2.0.
                codecPreferences: ["opus", "pcmu"],
                // Use fake DTMF tones client-side. Real tones are still sent to the other end of the call,
                // but the client-side DTMF tones are fake. This prevents the local mic capturing the DTMF tone
                // a second time and sending the tone twice. This will be default in 2.0.
                fakeLocalDTMF: true,
                    // Use `enableRingingState` to enable the device to emit the `ringing``
                    // state. The TwiML backend also needs to have the attribute`
                // `answerOnBridge` also set to true in the `Dial` verb. This option
                // changes the behavior of the SDK to consider a call `ringing` starting
                // from the connection to the TwiML backend to when the recipient of
                // the `Dial` verb answers.
                enableRingingState: true,
                debug: true,
            });

            device.on("ready", function (device) {
                log("Twilio.Device Ready!");
            });

            device.on("error", function (error) {
                log("Twilio.Device Error: " + error.message);
            });

            device.on("connect", function (conn) {
                log('Call currently in progress'); 
                console.log(conn.parameters.From)
                console.log(conn.parameters.To)
                if( !document.getElementById('callingTo').innerText ){
                    document.getElementById('callingTo').innerText = formatPhoneNumber(document.getElementById("phoneNumber").value.trim());
                }
                handleModal("modal-call-in-progress");
            });
            
            device.on("disconnect", function (conn) {
                let phoneNumber = conn.parameters.From;
                let toNumber = conn.parameters.To;
                stop()
                handleModal("modal-call-in-progress");
                document.getElementById("callingTo").innerText = "";
                log("Call ended.");
                var callDuration = document.getElementById('callDuration').innerHTML;
                var postData = {
                    duration: callDuration,
                    direction: conn.direction,
                    fromNumber: phoneNumber,
                    toNumber: toNumber,
                };/*
                $.ajax({
                    type: "POST",
                    url: "/save/log/call/", // Aquí debes poner la URL de tu endpoint en Python
                    data: postData,
                    success: function(response) {
                        console.log("Registro de llamada guardado exitosamente:", response);
                    },
                    error: function(err) {
                        console.error("Error al guardar el registro de la llamada:", err);
                    }
                });*/
            });

            device.on("incoming", function (conn) {
                console.log(conn.parameters.To)
                let toNumber = conn.parameters.To;
                let phoneNumber = toNumber.split(':')[1];
                device.audio.incoming(false);
                //log("Incoming connection from " + conn.parameters.From);
            
                // AJAX request to check if the number is configured for the subscription
                $.ajax({
                    url: '/check_number/',  // URL to the endpoint that will check the number
                    type: 'POST',
                    data: {
                        to_number: phoneNumber,
                        csrfmiddlewaretoken: '{{ csrf_token }}'  // Include CSRF token for Django
                    },
                    success: function(response) {
                        if (response.is_configured) {
                            document.getElementById("callerNumber").innerHTML = formatPhoneNumber(conn.parameters.From);
                            document.getElementById("callingTo").innerHTML = formatPhoneNumber(conn.parameters.From);
                            //document.getElementById("txtPhoneNumber").innerHTML = conn.parameters.From;
                            handleModal('modal-incomming-call')

                            const btnReject = document.getElementById('btnReject');
                            function rejectCall() {
                                handleModal('modal-incomming-call');
                                log("Rejected call ..."); 
                                conn.reject();
                                btnReject.removeEventListener('click', rejectCall);
                            }
                            btnReject.addEventListener('click', rejectCall);

                            const btnAcceptCalls = document.getElementById('btnAcceptCall');
                            function aceptCall() {
                                showCallDuration();
                                handleModal("modal-incomming-call");
                                console.log("Accepted call ..."); 
                                conn.accept(); 
                                btnAcceptCalls.removeEventListener('click', aceptCall);
                            }
                            btnAcceptCalls.addEventListener('click', aceptCall);
                            device.audio.incoming(true);
                        } else {
                            log("Number is not configured for this subscription.");
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error("Error checking the number configuration: ", error);
                    }
                });
            });

            device.on("cancel", function(conn) {
                log("Call cancelled by the caller.");
                const modalElement = document.getElementById("modal-incomming-call");
                if (modalElement && !modalElement.classList.contains("hidden")) {
                    handleModal("modal-incomming-call");
                }
                let phoneNumber = conn.parameters.From;
                let toNumber = conn.parameters.To
                var postData = {
                    duration: '0',
                    direction: "MISSING",
                    fromNumber: phoneNumber,
                    toNumber: toNumber,
                };/*
                $.ajax({
                    type: "POST",
                    url: "/save/log/call/", // Aquí debes poner la URL de tu endpoint en Python
                    data: postData,
                    success: function(response) {
                        console.log("Registro de llamada guardado exitosamente:", response);
                    },
                    error: function(err) {
                        console.error("Error al guardar el registro de la llamada:", err);
                    }
                });*/
            });


        })
        .catch(function (err) {
            console.log(err);
            log("Could not get a token from server!");
        });

    // Bind button to make call
    $('#btnDial').bind('click', function () {
        $('#modal-dial').modal('hide')
        // get the phone number to connect the call to
        var params = {
            To: document.getElementById("phoneNumber").value
        };

        // output destination number
        $("#txtPhoneNumber").text(params.To)
        

        console.log("Calling " + params.To + "...");
        if (device) {
            var outgoingConnection = device.connect(params);
            outgoingConnection.on("ringing", function () {
                log("Ringing...");
            });
        }
        document.getElementById('phoneNumber').innerHTML = "";

    })

     // Bind button to make call from customer section
     $('#btnCall').bind('click', function () {
        handleModal('modal-callconfirmation')

        // get customer name to show in the call in progress modal
        var customerName = document.getElementById("customerName").innerText;
        document.getElementById("callingTo").innerText = customerName;

        // get the phone number to connect the call to
        let phoneNumber = document.getElementById("customerPhoneNumber").value.trim();
        if (!phoneNumber.startsWith("+1")) {
            phoneNumber = "+1" + phoneNumber;
        }

        var params = {
            To: phoneNumber
        };

        // output destination number
        $("#txtPhoneNumber").text(params.To)

        console.log("Calling " + params.To + "...");
        if (device) {
            var outgoingConnection = device.connect(params);
            outgoingConnection.on("ringing", function () {
                log("Ringing...");
                showCallDuration();
            });
        }

    })

    // Bind button to hangup call

    $('.btnHangUp').bind('click', function () {
        //handleModal("modal-call-in-progress");
        log("Hanging up...");
        if (device) {
            device.disconnectAll();
        }
    })

    function formatPhoneNumber(phoneNumber) {
        // Elimina todos los caracteres que no sean dígitos
        phoneNumber = phoneNumber.replace(/\D/g, '');
    
        // Verifica si el número comienza con +1
        if (phoneNumber.startsWith('1')) {
            // Formato si el número comienza con +1
            return "+1 (" + phoneNumber.substring(1, 4) + ") " + phoneNumber.substring(4, 7) + "-" + phoneNumber.substring(7);
        } else {
            // Agrega +1 al principio y luego aplica el mismo formato
            phoneNumber = "1" + phoneNumber;
            return "+1 (" + phoneNumber.substring(1, 4) + ") " + phoneNumber.substring(4, 7) + "-" + phoneNumber.substring(7);
        }
    }
    
    // Activity log
    function log(message) {
        var logDiv = document.getElementById("callingLog");
        logDiv.innerHTML =  message;
        //logDiv.scrollTop = logDiv.scrollHeight;
        console.log(message)
    }

    function handleModal(modalId) {
        const modal = document.getElementById(modalId);
        const backdrop = document.getElementById(`${modalId}-backdrop`);
        if (modal) {
            modal.classList.toggle("hidden");
            modal.classList.toggle("flex");
        }
        if (backdrop) {
            backdrop.classList.toggle("hidden");
            backdrop.classList.toggle("block");
        }
    }

     ///////////////       CALL IN PROGRESS MODAL          ////////////////////////////


     document.getElementById('modal-call-in-progress').addEventListener('show.bs.modal', function() {
        showCallDuration();
    });
    
    var time;
    function showCallDuration() {

        var output = document.getElementById('callDuration');
        var ms = 0;
        var sec = 0;
        var min = 0;

        function timer() {
            ms++;
            if (ms >= 100) {
                sec++;
                ms = 0;
            }
            if (sec === 60) {
                min++;
                sec = 0;
            }
            if (min === 60) {
                ms = 0;
                sec = 0;
                min = 0;
            }
    
            var milli = ms < 10 ? '0' + ms : ms;
            var seconds = sec < 10 ? '0' + sec : sec;
            var minute = min < 10 ? '0' + min : min;
    
            var timer = minute + ':' + seconds;
            output.innerHTML = timer;
        }
    
        // Start timer
        function start() {
            time = setInterval(timer, 10);
        }
    
        // Stop timer
        function stop() {
            console.log("entro al stop")
            clearInterval(time);
        }
    
        // Reset timer
        function reset() {
            ms = 0;
            sec = 0;
            min = 0;
    
            output.innerHTML = '00:00:00';
        }
    
        // Start the timer
        start();
    
        document.getElementById('modal-call-in-progress').addEventListener('hidden.bs.modal', function() {
            console.log('entro aqui')
            stop();
        });
    }

    function stop() {
        clearInterval(time);
    }

});
