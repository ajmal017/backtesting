
/**
 * Backtesting
 * 
 */


var Backtesting = function(){};

Backtesting.prototype.url = 'http://'+location.host;
Backtesting.prototype.uglyTimeout = {};
Backtesting.prototype.handleLogin = {
    loggedIn:false,
    accessToken:'',
    refreshToken: ''
};

Backtesting.prototype.portfolioValue = {};
Backtesting.prototype.portfolioValue2 = {};
Backtesting.prototype.setLocalStorage = function(){
    var _self = this;
    if (Storage){
        localStorage.setItem("access_token", _self.handleLogin.accessToken);
        localStorage.setItem("refresh_token", _self.handleLogin.refreshToken);
    }else{
        return false;
    }   
};

Backtesting.prototype.getLocalStorage = function(item){
    var _self = this;
    if (Storage){
    var storage = localStorage.getItem(item);
    return storage;
    } else {
        return false;
    }
    
};

Backtesting.prototype.removeLocalStorage = function(){
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
};

Backtesting.prototype.readLocalStorage = function(){
    var _self = this;   
    var access = localStorage.getItem("access_token");
    var refresh = localStorage.getItem("refresh_token");
    if (!!access && !! refresh){
        _self.handleLogin.accessToken = access;
        _self.handleLogin.refreshToken = refresh;
        _self.handleLogin.loggedIn = true;
        _self.useRefreshToken();
        _self.loadCredentials();
        _self.loadPortfolios();
    }
};
Backtesting.prototype.useRefreshToken = function(){
    var _self = this;
    console.log('ask for refresh '+ Date.now());
    $.ajax({
        type: "POST",
        url: `${_self.url}/token/refresh`,
        headers: {
            'Content-Type':'Application/JSON',
            'Authorization':'Bearer ' + _self.handleLogin.refreshToken,
            "Access-Control-Allow-Origin":_self.url,
            "Access-Control-Allow-Methods":"POST",
            "Access-Control-Allow-Headers":"Content-Type"
        },
        data:JSON.stringify({user:"edasikoy"}),
        success: function(data){
            _self.handleLogin.accessToken = data["access_token"];
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {           
            if (errorThrown == 'UNAUTHORIZED'){
                _self.handleLogin.loggedIn = false;
                _self.navigateToLogIn();
                _self.showLoginMessage("Please log in!");
            }
        }
    });
}
Backtesting.prototype.request = function(url, type, load, success, handleError ){
    var _self = this;
    var succeed = success();
    $.ajax({
        type: type,
        url: _self.url + url,
        headers: {
            'Content-Type':'Application/JSON',
            'Authorization':'Bearer ' + _self.handleLogin.accessToken,
            "Access-Control-Allow-Origin":_self.url,
            "Access-Control-Allow-Headers":"Content-Type"
        },
        data:load,
        success: succeed,
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            console.log('error on 1st request ' + Date.now());
            if (errorThrown == 'UNAUTHORIZED'){
                console.log("unauthorized message in refresh "+ Date.now());
                $.ajax({
                    type: "POST",
                    url: `${_self.url}/token/refresh`,
                    headers: {
                        'Content-Type':'Application/JSON',
                        'Authorization':'Bearer ' + _self.handleLogin.refreshToken,
                        "Access-Control-Allow-Origin":_self.url,
                        "Access-Control-Allow-Methods":"POST",
                        "Access-Control-Allow-Headers":"Content-Type"
                    },
                    data:JSON.stringify({user:"edasikoy"}),
                    success: function(data){
                        var access = data["access_token"];
                        _self.handleLogin.accessToken = access;
                        $.ajax({
                            type: type,
                            url: _self.url + url,
                            headers: {
                                'Content-Type':'Application/JSON',
                                'Authorization':'Bearer ' + access,
                                "Access-Control-Allow-Origin":_self.url,
                                "Access-Control-Allow-Headers":"Content-Type"
                            },
                            data:load,
                            success: succeed,
                            error:function(XMLHttpRequest, textStatus, errorThrown) {
                                console.log('final error ' + Date.now());
                                if (handleError){
                                    console.log("handling final error "+ Date.now())
                                    handleError();
                                }else{
                                    console.log("popup on final error " + Date.now())
                                    _self.popUpMessage(errorThrown);
                                }                            
                                
                            }                       
                        });
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        if (errorThrown == 'UNAUTHORIZED'){
                            console.log('unauthorized message after refresh try '+ Date.now());
                            _self.handleLogin.loggedIn = false;
                            _self.navigateToLogIn();
                            _self.showLoginMessage("Please log in!");
                        }else if (handleError){
                                console.log("handling 2nd error "+ Date.now());
                                handleError();
                        }else{
                            console.log('popup on 2nd fail '+ Date.now());
                            _self.popUpMessage(errorThrown);
                        }
                    }
                });
            }else if(erorrThrown=="INTERNAL SERVER ERROR"){
                 console.log("Internal server error on first attend "+ Date.now());
                _self.useRefreshToken();
                _self.popUpMessage(errorThrown);
            } else if (handleError){
                handleError();
                console.log("handling 1st error "+ Date.now());
            }else {
                console.log("popup on 1st fail "+ Date.now());
                _self.popUpMessage(errorThrown);
            }
        }
    });
};

Backtesting.prototype.getHeader = function(){
    var _self = this;
    return {
        'Content-Type':'Application/JSON',
        'Authorization':'Bearer ' + _self.handleLogin.accessToken,
        "Access-Control-Allow-Origin": _self.url,
        "Access-Control-Allow-Methods":"GET",
        "Access-Control-Allow-Headers":"Content-Type"
    }
};
Backtesting.prototype.dappa = {};
Backtesting.prototype.backtestingSpecialType = "";

Backtesting.prototype.length = function(object){
    counter = 0;
    for (var key in object) {
        counter++;
    }

    return counter;
};
Backtesting.prototype.createElement = function(name, properties, htm){
    var element = document.createElement(name);
    if (properties){
        $(element).attr(properties);
        if (htm){
            $(element).html(htm);
        }
    }
    return element;
};
Backtesting.prototype.createBox = function(key, value){
    var _self = this;
    var legend = key.replace(/\s+|\:/g,'');
    var holder = _self.createElement('span', {class: legend + '-line portfolio-lines'});
    var keyElement = _self.createElement('span',{class: legend +'-key portfolio-keys portfolio-cells'}, key);
    var valueElement = _self.createElement('span', {class:legend + '-value portfolio-values portfolio-cells'}, value);
    holder.append(keyElement);
    holder.append(valueElement);
    return holder;
};
Backtesting.prototype.createPortfolioBoxes = function(boxes){
    var _self = this;
    var holder = _self.createElement('div',{id:"porfolio-box-holder",class:"portfolio-box-holders"});
    var length = boxes.portfolios.length;
    for (var i = 0; i<length ;i ++){
        var box = boxes.portfolios[i];
        var singleBox = _self.createElement('div',{id:"single-box",class:"single-box"});
        var starting = new Date(parseInt(box.start))
        var start = _self.createBox("Starting at: ",starting.toString().substr(4,18));
        var ending = new Date(parseInt(box.start))
        var end = _self.createBox("Ending at: ", ending.toString().substr(4,18));
        var portfolio = _self.createBox("Portfolio: ", "$" + box.portfolio);
        var roi = _self.createBox("ROI: ", box.roi + "%");
        var profit = _self.createBox("Profit: ", box.profit + "$");
        var name = _self.createBox("Name: ", box.name);
        var currencies = box.coins.substr(0,box.coins.length-1).split(',');
        var cweigths = box.weights.substr(0,box.weights.length-1).split(',');
        var basket = '';
        for (j=0;j<cweigths.length;j++){
            basket += currencies[j] +':' + cweigths[j] +'% '
        }
        var coins = _self.createBox('coins', basket);
        var closeButton = _self.createElement('button',{id:"delete"+(i+1),class:"portfolio-delete-button buttons"},"delete");
        singleBox.append(name);
        singleBox.append(portfolio);
        singleBox.append(roi);
        singleBox.append(coins)
        singleBox.append(start);
        singleBox.append(end);
        singleBox.append(profit);
        singleBox.append(closeButton);
        holder.append(singleBox);
        
    }
    return holder;
};
Backtesting.prototype.appendPortfolioDeletion = function(){
    var _self = this;
    $('.tab-pane').on('click',".portfolio-delete-button",function(){
        var deleteId = $(this).attr('id').replace("delete","");
        var toSend = JSON.stringify({portfolio:"edasikoe"});
        _self.request(`/portfolio/${deleteId}`,'DELETE',toSend, function(){
            return function(data){
                _self.loadPortfolios();
            }
        });
    });
};

Backtesting.prototype.getCurrencies = function(){

    var _self = this;
    var currencyInput = $('input[name="currency"]')
    //Choose Suggested Coins
    $('.suggestions').on('click', '.suggestion', function () {
        var value = $(this).data('value');
        currencyInput.val(value.toUpperCase())
        $('.suggestions').css('display', 'none');
    });
    
    //send request on keyup to Api. Api retuns suggested coins 
    currencyInput.keyup(function() {
        var value = $(this).val().toUpperCase()
        if (!value){
            $('.suggestions').empty().css('display', 'none');

            return false;
        }
        var daka = {q: value};
        $.ajax({
            type:"GET",
            //url: `http://localhost:5000/coin?q=${value}`,
            url: `${_self.url}/coin`,
            data: {q: value},
            success: function(data) {
                $('.suggestions').empty().css('display', 'block').append(function(){
                    var html = '';
                    for ( var key in data ){
                        html += "<div data-value='"+key+"' class='suggestion'><b style='font-size: 25px;'>" + key + "</b> | " + data[key] + "</div>"
                    }
                    return html
                });
            }
        })
    });
};
Backtesting.prototype.postCurrencies = function(){

    var _self = this;
    var currencyInput = $('input[name="currency"]')
    //Choose Suggested Coins
    $('.suggestions').on('click', '.suggestion', function () {
        var value = $(this).data('value');
        currencyInput.val(value.toUpperCase())
        $('.suggestions').css('display', 'none');
    });
    
    //send request on keyup to Api. Api retuns suggested coins 
    currencyInput.keyup(function() {
        var value = $(this).val().toUpperCase()
        if (!value){
            $('.suggestions').empty().css('display', 'none');

            return false;
        }
        var daka = {q: value};
        $.ajax({
            type: "POST",
            //url: `http://localhost:5000/coin?q=${value}`,
            url: `${_self.url}/coin`,
            data: {q: value},
            contentType: "Application/JSON",
            success: function(data) {
                $('.suggestions').empty().css('display', 'block').append(function(){
                    var html = '';
                    for ( var key in data ){
                        html += "<div data-value='"+key+"' class='suggestion'><b style='font-size: 25px;'>" + key + "</b> | " + data[key] + "</div>"
                    }
                    return html
                });
            }
        })
    });
};

Backtesting.prototype.coinSelection = function(){
    var _self = this;
    $('#submit').on('click',function(event){
        var percentage = $('#percent');
        //event.preventDefault()
        var element = $('#selection-form');
        var currencySelection = element.find('input[name="currency"]'); 
        var currency = $(currencySelection).val();
        //var currency = element.find('input[name="currency"]').val() != "" ? element.find('input[name="currency"]').val() : "BTC";
        if ($(currencySelection).val()==''){
            _self.popUpMessage("Please select a currency and its corresponding weight");
            return false;
        }
        var percent = element.find('input[name="percent"]');
        if ($(percent).val()==''){
            _self.popUpMessage("Please select the weight of "+currency);
            return false;
        }
        if(!_self.dappa[currency]){
            if (percent.prop('max')-parseFloat(percent.val())>=0){
                percent.prop('max', percent.attr('max') - parseFloat(percent.val()));
            
                if(_self.dappa[currency]){
                    _self.dappa[currency] = parseFloat(percent.val()) + _self.dappa[currency];
                }else{
                    _self.dappa[currency] = parseFloat(percent.val());
                }
                $('#selected-items').append('<span coin="'+currency+'" percent="'+_self.dappa[currency]+'" class="selected-item addedCoin">'+ currency + " | " + _self.dappa[currency] +'% <img width="15px" class="close-button" src="https://www.freeiconspng.com/uploads/close-button-png-23.png" /></span>');
                $('input[name="percent"]').val('');
                $('input[name="currency"]').val('');
                $("#run-backtesting").removeClass("unavailable");
                
            }else{
                _self.popUpMessage("There are "+parseFloat(percent.prop('max'))+"% left to 100%");
            }
            
        }else {
            _self.popUpMessage(currency + " is already in use.");
        }
        var rest = percent.prop('max');
        $('#allocated').val(100-parseFloat(rest)+'%');
        $('#allocated').css('width',((100- parseFloat(rest))/100*74 +26)+'%');
    })

};
Backtesting.prototype.coinRemoval = function(){
    var _self = this;
    $('#selected-items').on('click', '.close-button', function() {
        $('#errorMessage').hide();
        element = this.parentElement;
        index = element.getAttribute('coin');
        percent = element.getAttribute('percent');
        var whole = $('input[name="percent"]');
        whole.prop('max', function(){
            return parseFloat(whole.prop('max')) + parseFloat(percent);
        });
        delete _self.dappa[index];
        if(!_self.length(_self.dappa)){
            $('#run-backtesting').addClass('unavailable');
        }
        if(!_self.length(_self.dappa)){
            $('#save-portfolio').addClass('unavailable');
        }

        this.parentElement.remove();
        $('#allocated').val(100-whole.prop('max')+'%');
        $('#allocated').css('width',(100-parseFloat(whole.prop('max')))/100*74+26+'%');
        $('#container').empty('');
        $('#portfolio-end').text('$ 0');
        $('#ROI-end').text('0%');
        $('#fees-end').text('$ 0.0');
        var store = $('#save-portfolio');
        if (!$(store).hasClass('unavailable')){
            $('#save-portfolio').addClass('unavailable');
        }
        var confirmation = $('#save-confirmation')
        if(!$(confirmation).hasClass('unavailable')){
            $('#save-confirmation').addClass('unavailable');
        }
        
    });
};
Backtesting.prototype.showLoginMessage = function(message){
    var _self = this;
    var holder = $('#login-message');
    $(holder).text(message);
    $(holder).css('visibility','visible');
    setTimeout(function(){
        $(holder).css('visibility','hidden');
        //$(holder).text('');
    }, 4000);
};
Backtesting.prototype.showMessage = function(message, place, callback){
    var _self = this;
    var holder = $('#'+place);
    $(holder).text(message);
    $(holder).addClass("active");
    setTimeout(function(){
        $(holder).removeClass("active");
        if (callback){
            callback();
        }
    }, 3000);
};
Backtesting.prototype.popUpMessage = function(message){
    var background = $('.backgroundMessage');
    var popup = $('#popup-message');
    var text = $('#error-text');
    $(text).text(message);
    $(popup).addClass("active");
    $(background).addClass('active');
};
Backtesting.prototype.hideMessage = function(callback){
    var background = $('.backgroundMessage');
    var popup = $('#popup-message');
    var text = $('#error-text');
    $(popup).removeClass("active");
    $(background).removeClass("active");
    //$(text).text('');
    if (callback){
        callback();
    }
};
Backtesting.prototype.hideBackground = function(){
    $('.backgroundMessage').on('click',function(){
        $('.backgroundMessage').removeClass('active');
        $('.popups').removeClass('active');
    });
};
Backtesting.prototype.hidePopUp = function(){
    var _self = this;
    $('#ok-button').on('click',function(){
        _self.hideMessage();
    });
};
Backtesting.prototype.popItUp = function(selector){
    $('.backgroundMessage').addClass("active");
    $(selector).addClass("active");
};
Backtesting.prototype.popItDown = function(selector){
    $('.backgroundMessage').removeClass("active");
    $(selector).removeClass("active");
};

Backtesting.prototype.navigateToLogIn = function(){
    $('li').removeClass("active");
    $('.pages').removeClass("active");
    $('.pages').removeClass("in");
    $('#logIn-tab').addClass("active");
    $("#logIn").addClass("in active");
    $("html, body").animate({ scrollTop: 0 }, "slow");
};

Backtesting.prototype.savePortfolio = function(){
    var _self = this;
    var confirmation = $('#save-confirmation');
    $('#save-portfolio').on('click',function(){
        if (!_self.handleLogin.loggedIn){
            _self.navigateToLogIn();
            _self.showLoginMessage("Please log in or register");
            return false;
        }
        _self.popItUp('#save-confirmation');
    });
    $('#save-portfolio-cancelation').on('click',function(){
        _self.popItDown('#save-confirmation');
    });
    $('#save-portfolio-confirmation').on('click',function(){
        
        var name = $('#portfolio-name').val();
        if (name == '' || name == undefined){
            _self.popUpMessage('Please name your Portfolio!');
        }
        _self.popItDown('#save-confirmation');
        var kapa = _self.portfolioValue;
        kapa.name = name;
        var kaka = JSON.stringify(kapa);

        _self.request('/portfolio','POST',kaka,function(){
            return function(data){
                if (data['message']){
                     _self.popUpMessage(data['message']);
                    _self.loadPortfolios();
                }
            }
        }); 
    });
};
Backtesting.prototype.savePortfolio2 = function(){
    var _self = this;
    var confirmation = $('#save-confirmation2');
    $('#save-portfolio2').on('click',function(){
        if (!_self.handleLogin.loggedIn){
            _self.navigateToLogIn();
            _self.showLoginMessage("Please log in or register");
            return false;
        }
        _self.popItUp(confirmation);
    });
    $('#save-portfolio-cancelation2').on('click',function(){
        _self.popItDown(confirmation);
    });
    $('#save-portfolio-confirmation2').on('click',function(){
        var name = $('#portfolio-name2').val();
        if (name == '' || name == undefined){
            _self.popUpMessage('Please name your Portfolio!');
        }
        _self.popItDown(confirmation);
        var kapa = _self.portfolioValue2;
        kapa.name = name;
        var kaka = JSON.stringify(kapa);
        _self.request('/portfolio','POST',kaka,function(){
            return function(data){
                if (data['message']){
                    _self.popUpMessage(data['message']);
                    _self.loadPortfolios();
                }
            }
        }); 
    });
};
Backtesting.prototype.loadPortfolios = function(){
    var _self = this;
    var portfolios = {};
        $.ajax({
            type:"GET",
            url:`${_self.url}/portfolio`,
            headers: _self.getHeader(),
            success:function(data){
                var elha = document.getElementById("v-pills-savedPortfolios");
                $(elha).html('');
                elha.append(_self.createPortfolioBoxes(data));

            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if (errorThrown == 'UNAUTHORIZED'){
                    //_self.useRefreshToken();
                    //_self.navigateToLogIn();
                    //_self.showLoginMessage("Please log in or register");
                }
            }
        });
};

Backtesting.prototype.loadCredentials = function(){
    var _self = this;
        $.ajax({
            type:"GET",
            url:`${_self.url}/user`,
            headers: _self.getHeader(),
            success:function(data){
                $('#emailSettings').val(data['email']);
                $('#firstnameSettings').val(data['firstname']);
                $('#lastnameSettings').val(data['lastname']);
            }
        });
};
Backtesting.prototype.editPassword = function(){
    var _self = this;
    $("#edit-password").on('click',function(){
        var passwordSet = $('#password-set');
        if ($(passwordSet).hasClass("active")){
            $(passwordSet).removeClass("active");
        } else {
            $(passwordSet).addClass("active");
        }
    })
};
Backtesting.prototype.changePassword = function(){
    var _self = this;
    $('#change-password').on('click',function(){
        if (!_self.handleLogin.loggedIn){
            _self.navigateToLogIn();
            _self.showLoginMessage("Please log in or register");
            return false;
        }
        var oldPass = $('#oldPasswordSettings').val();
        var newPass = $('#newPasswordSettings').val();
        var confirmPass = $('#confirmNewPasswordSettings').val();
        if (newPass !== confirmPass){
            _self.popUpMessage("Passwords doesn't match!");
        } else {
            var sendData = JSON.stringify({password:oldPass,newpassword:newPass});
            _self.request('/changepassword','PUT',sendData,function(){
                return function(data){
                    _self.popUpMessage(data["message"]);
                    $('#password-set').removeClass('active');
                }
            });
        }
    });
};
Backtesting.prototype.editEmail = function(){
    var _self = this;
    var button = $('#change-email');
    $(button).on('click',function(){
        if (!_self.handleLogin.loggedIn){
            _self.navigateToLogIn();
            _self.showLoginMessage("Please log in or register");
            return false;
        }
        var input = $('#emailSettings');
        if ($(input).prop('readonly')){
            $(input).prop('readonly',false);
            $(input).focus();
            $(button).text('Save');
        } else {
            var sendData = JSON.stringify({email:$(input).val()});
            _self.request('/user/email','PUT',sendData, function(){
                return function(data){
                    _self.popUpMessage(data["message"]);
                    $('#emailSettings').prop('readonly',true);
                    $('#change-email').text('Change');
                }
            }, function(){
                $('#emailSettings').prop('readonly',true);
                $('#change-email').text('Change');
            });
        }
    });
};
Backtesting.prototype.editFirstname = function(){
    var _self = this;
    var button = $('#change-firstname');
    $(button).on('click',function(){
        if (!_self.handleLogin.loggedIn){
            _self.navigateToLogIn();
            _self.showLoginMessage("Please log in or register");
            return false;
        }
        var input = $('#firstnameSettings');
        if ($(input).prop('readonly')){
            $(input).prop('readonly',false);
            $(input).focus();
            $(button).text('Save');
        } else {
            var sendData = JSON.stringify({firstname:$(input).val()});
            _self.request('/user/firstname','PUT',sendData,function(){
                return function(data){
                    _self.popUpMessage(data["message"]);
                    $('#firstnameSettings').prop('readonly',true);
                    $('#change-firstname').text('Change');
                }
            }, function(){
                    $('#firstnameSettings').prop('readonly',true);
                    $('#change-firstname').text('Change');
            });
        }
    });
};
Backtesting.prototype.editLastname = function(){
    var _self = this;
    var button = $('#change-lastname');
    $(button).on('click',function(){
        if (!_self.handleLogin.loggedIn){
            _self.navigateToLogIn();
            _self.showLoginMessage("Please log in or register");
            return false;
        }
        var input = $('#lastnameSettings');
        if ($(input).prop('readonly')){
            $(input).prop('readonly',false);
            $(input).focus();
            $(button).text('Save');
        } else {
            var sendData = JSON.stringify({lastname:$(input).val()});
            _self.request('/user/lastname','PUT',sendData,function(){
                return function(data){
                    _self.popUpMessage(data["message"]);
                    $('#lastnameSettings').prop('readonly',true);
                    $('#change-lastname').text('Change');
                }
            }, function(){
                    $('#lastnameSettings').prop('readonly',true);
                    $('#change-lastname').text('Change');
            });
        }
    });
};


// YOUR ALLOCATIONS COLUMN

Backtesting.prototype.saveAllocations = function(){
    var _self = this;
    var yourAllocations = $('.allocations2');

    // When clicking add this happens:
    $('.addButton').on('click', function(event) {
        var allocatedCurrency = $('#allocateCurrency').val();
        var allocatedPercent = $('#allocatePercent').val();

        yourAllocations.append('<div class="row myAllocations">' + '<div class="col-sm myAllocatedCurrency">' + '<span>' 
        + allocatedCurrency + '</span>' + '</div>' + ": " 
        + '<div class="col-sm myAllocatedPercentage">' + '<span>' + allocatedPercent + "%" + '</span>' + '</div>' + '</div>');
        yourAllocations.append('<div class="form-group saveAllocation">' +                          
        '<input type="submit" value="Save as current portfolio" class="buttons saveAllocated" id="saveAllocated"/>' 
        + '</div>')

        $('.saveAllocated').on('click', function(event) {
            $('.dashboard').append('<div class="row myPortfolio">' + '<div class="col-sm myCoin">' + '<span>' 
            + allocatedCurrency + '</span>' + '</div>' + ": " 
            + '<div class="col-sm myCoinPercentage">' + '<span>' + allocatedPercent + "%" + '</span>' + '</div>' + '</div>')
            $('.dashboard').append('<div class="form-group rebalancing">' +                          
            '<input type="submit" value="Rebalance Now" class="buttons rebalance" id="rebalance"/>' 
            + '</div>')
        })
        
    });

};

// LOGIN/REGISTER FORM Effects
Backtesting.prototype.registerFormEffects = function(){
    $('#login-form-link').click(function(e) {
        $("#login-form").delay(100).fadeIn(100);
        $("#register-form").fadeOut(100);
        $('#register-form-link').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
    });
    $('#register-form-link').click(function(e) {
        $("#register-form").delay(100).fadeIn(100);
        $("#login-form").fadeOut(100);
        $('#login-form-link').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
    });

    $('btn-login').on('click', function(event) {
         $('#home').show();
        $('#logIn').hide();

    });
};
Backtesting.prototype.register = function(){
    var _self = this;
    $('#register-form').submit(function(e){
        e.preventDefault();
        var user = $('#username');
        var username = $(user).val();
        var pass = $('#password');
        var password = $(pass).val();
        var confirmPass = $('#confirm-password');
        var confirmPassword = $(confirmPass).val();
        var mail = $('#email');
        var email = $(mail).val();
        var message = $('#registration-message');
        if (password != confirmPassword){
            message.text("Passwords don't match!");
            return false;
        }
        if (username.length < 4){
            message.text("Username must be longer than 3 characters!");
            return false;
        }
        if (email == ''|| email == undefined){
            message.text("E-mail is mandatory");
            return false;
        }
        var data = {
            username:username,
            password:password,
            email:email
        };
        $.ajax({
            type:'POST',
            url: `${_self.url}/registration`,
            contentType: 'Application/JSON',
            data: JSON.stringify(data),
            success: function(data){
                console.log(data);
                var answer = data//JSON.parse(data);
                message.text(answer.message);
                if (answer.access_token){
                    //_self.handleLogin.accessToken = answer.access_token;
                    //_self.handleLogin.refreshToken = answer.refresh_token;
                    //_self.handleLogin.loggedIn = true;
                     console.log(_self.handleLogin);
                     $(user).val('');
                     $(pass).val('');
                     $(confirmPass).val('');
                     $(mail).val('');
                }                
            }
        });

    });
};

Backtesting.prototype.login = function(){
    var _self = this;
    $('#login-form').submit(function(e){
        e.preventDefault();
        var user = $('#login-username');
        var username = $(user).val();
        var pass = $('#login-password');
        var password = $(pass).val();
        var data = {
            username:username,
            password:password
        };
        $.ajax({
            type:'POST',
            url: `${_self.url}/login`,
            contentType: 'Application/JSON',
            data: JSON.stringify(data),
            success: function(data){
                var answer = data;
                _self.showLoginMessage(answer.message);
                if (answer.access_token){
                    _self.handleLogin.accessToken = answer.access_token;
                    _self.handleLogin.refreshToken = answer.refresh_token;
                    _self.handleLogin.loggedIn = true;
                   _self.loadPortfolios();
                   _self.loadCredentials();
                   _self.setLocalStorage();                   
                   $(user).val('');
                   $(pass).val('');
                }                
            }
        });

    });

}
Backtesting.prototype.logout = function(){
    var _self = this;
    $("#sign-out").on('click',function(){
        $('#porfolio-box-holder').html('');
        if (_self.handleLogin.loggedIn == true){
            var kaka = JSON.stringify({user:"edasikoy"});
            _self.request('/logout/access','POST',kaka,function(){
                return function(data){
                    if (data.message == "Access token has been revoked"){
                        $.ajax({
                            type: "POST",
                            url: `${_self.url}/logout/refresh`,
                            headers: {
                                'Content-Type':'Application/JSON',
                                'Authorization':'Bearer ' + _self.handleLogin.refreshToken,
                                "Access-Control-Allow-Origin":_self.url,
                                "Access-Control-Allow-Methods":"POST",
                                "Access-Control-Allow-Headers":"Content-Type"
                            },
                            data:JSON.stringify({user:"edasikoy"}),
                            success: function(data){
                                if (data.message = "Refresh token has been revoked"){
                                    _self.removeLocalStorage();
                                    _self.handleLogin.accessToken = "";
                                    _self.handleLogin.refreshToken = "";
                                    _self.handleLogin.loggedIn = false;
                                    $('#emailSettings').val('');
                                    $('#firstnameSettings').val('');
                                    $('#lastnameSettings').val('');
                                    _self.showLoginMessage("Signed out successfully.");
                                } else {
                                    //console.log(data["message"]);
                                }
                            }
                        });
                    } else {
                        //console.log(data["message"]);
                    }
                }
            });
        }
    });
};
Backtesting.prototype.forgotPassword = function(){
    var _self = this;
    $('.forgot-password').on('click',function(){
        if (_self.handleLogin.loggedIn !== true){
            _self.popItUp('#forgotten-password');
        }        
    });
    $('#reset-pass-cancelation').on('click',function(){
        _self.popItDown('#forgotten-password');
    });
    $('#reset-new-pass').on('click',function(){
        var umail = $('#new-pass').val();
        _self.popItDown('#forgotten-password');
        var toSend = JSON.stringify({email:umail});
        $.ajax({
            type: "POST",
            contentType:"Application/JSON",
            url: `${_self.url}/forgottenpassword`,
            data:toSend,
            success: function(data){
                var message = '';
                if (data['msg']){
                    message = data['msg'];
                } else if (data['message']){
                    message = data['message'];
                }
                $('#new-pass').val("");
                if(message){
                    _self.popUpMessage(message);
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                _self.popUpMessage("Something went wrong. Please try again.");   
            }


        });
    });
};
Backtesting.prototype.askForVerification = function(){
    var _self = this;
    $('#ask-verification').on('click',function(){
        if (_self.handleLogin.loggedIn == true){
            $.ajax({
                type: "GET",
                url: `${_self.url}/verification`,
                headers: _self.getHeader(),
                success: function(data){
                    if (data['msg']){
                        _self.popUpMessage(data['msg']);
                    }else {
                        _self.popUpMessage(data['message']);
                    }                    
                },
                error: function(data){
                    if(data["msg"]){
                        _self.popUpMessage(data['msg']);
                    }else{
                        _self.popUpMessage(data['message']);
                    }
                   
                }
            })
        }
    })
};
//run backtesting and set weights according to MarketCap 
Backtesting.prototype.byMarketCap = function(){
    var _self = this;
    //Use distribution by market cap
    $('#byMarketCap').on('click', function(event){
        $('#container2').html('');
        var starting = $('#start-date2');
        var start = $(starting).val();
        var ending = $('#end-date2');
        var end = $(ending).val();
        var portfolioInput = $('#portfolio2'); 
        var portfolio = $(portfolioInput).val();
        var intervalInput = $('#interval2');
        var interval = $(intervalInput).val();
        if (!interval){
            interval = 24;
        }
        var coins = $('#coins-number');
        var coinsNumber = $(coins).val();
        if(!start || !end || !portfolio || !coinsNumber){
            if(!start){
                $(starting).focus();
            } else if (!end){
                $(ending).focus();
            } else if (!portfolio){
                $(portfolioInput).focus();
            } else if(!coinsNumber){
                $(coins).focus();
            }
            return false;
        }
        var startingEpoch = new Date(start).getTime()
        var endingEpoch = new Date(end).getTime()
        if (startingEpoch >= endingEpoch){
            _self.popUpMessage("The starting time must be before the ending time!");
            return false;
        }else if(endingEpoch-startingEpoch > 2000 * 60 * 60 * 1000){
             _self.popUpMessage("The maximum allowed interval is 2000 hours!");
             return false;     
        }
        $('#results2').show();
        _self.portfolioValue2 = {start: startingEpoch, end: endingEpoch, portfolio: portfolio, interval:interval}
        var dakata = {
                start: startingEpoch, 
                end: endingEpoch, 
                portfolio: portfolio, 
                interval:interval, 
                cnumber:coinsNumber
            };
        daga = JSON.stringify(dakata);
        $('#save-portfolio2').removeClass('unavailable');
        _self.backtestingSpecialType = "by Market Cap";
        $.ajax({
            type:'POST',
            url:`${_self.url}/backtesting/marketcap`,
            contentType:"Application/JSON",
            data: daga,
            success: _self.drawGraph('2','container2')
        })
    });
};

Backtesting.prototype.equalyWeighted = function(){
    var _self = this;
    //Use distribution by market cap
    $('#equalyWeighted').on('click', function(event){
        $('#container2').html('');
        var starting = $('#start-date2');
        var start = $(starting).val();
        var ending = $('#end-date2');
        var end = $(ending).val();
        var portfolioInput = $('#portfolio2'); 
        var portfolio = $(portfolioInput).val();
        var intervalInput = $('#interval2');
        var interval = $(intervalInput).val();
        var coins = $('#coins-number');
        var coinsNumber = $(coins).val();
        if(!start || !end || !portfolio || !interval || !coinsNumber){
            if(!start){
                $(starting).focus();
            } else if (!end){
                $(ending).focus();
            } else if (!portfolio){
                $(portfolioInput).focus();
            } else if (!interval){
                $(intervalInput).focus();
            } else if(!coinsNumber){
                $(coins).focus();
            }
            return false;
        }
        var startingEpoch = new Date(start).getTime()
        var endingEpoch = new Date(end).getTime()
        if (startingEpoch >= endingEpoch){
            _self.popUpMessage("The starting time must be before the ending time!");
            return false;
        }else if(endingEpoch-startingEpoch > 2000 * 60 * 60 * 1000){
             _self.popUpMessage("The maximum allowed interval is 2000 hours!");
             return false;     
        }
        $('#results2').show();
        _self.portfolioValue2 = {coins: {first: coinsNumber + " equaly weighted."}, start: startingEpoch, end: endingEpoch, portfolio: portfolio, interval:interval}
        var dakata = {
                start: startingEpoch, 
                end: endingEpoch, 
                portfolio: portfolio, 
                interval:interval, 
                cnumber:coinsNumber
            };
        daga = JSON.stringify(dakata);
        _self.backtestingSpecialType = "Equaly weighted"
        $('#save-portfolio2').removeClass('unavailable');
        $.ajax({
            type:'POST',
            url:`${_self.url}/backtesting/equalyweighted`,
            contentType:"Application/JSON",
            data: daga,
            success: _self.drawGraph('2','container2')
        })
    });
};
//run the Backtesting engine from server
Backtesting.prototype.runBacktesting = function(){
    var _self = this;   
    $('.run').click(function() {
        $('#container').html('');
        var percentage = $('#percent');
        if ($(percentage).prop('max') =='100'){
            _self.popUpMessage("Please select a currency and its corresponding weight");
            return false;
        }
        var starting = $('#start-date');
        var start = $(starting).val();
        var ending = $('#end-date');
        var end = $(ending).val();
        var portfolioInput = $('#portfolio'); 
        var portfolio = $(portfolioInput).val();
        var intervalInput = $('#interval');
        var interval = $(intervalInput).val();
        if(!start || !end || !portfolio || !interval){
            if(!start){
                $(starting).focus();
            } else if (!end){
                $(ending).focus();
            } else if (!portfolio){
                $(portfolioInput).focus();
            } else if (!interval){
                $(intervalInput).focus();
            }
            return false;
        }
        var startingEpoch = new Date(start).getTime();
        var endingEpoch = new Date(end).getTime();
        if (startingEpoch >= endingEpoch){
            _self.popUpMessage("The starting time must be before the ending time!");
            return false;
        }else if(endingEpoch-startingEpoch > 2000 * 60 * 60 * 1000){
             _self.popUpMessage("The maximum allowed interval is 2000 hours!")
             return false;     
        }
        $('#results').show();
        var kapa = {coins: _self.dappa, start: startingEpoch, end: endingEpoch, portfolio: portfolio, interval:interval}
        var kaka = JSON.stringify(kapa);
        _self.portfolioValue = {start: startingEpoch, end: endingEpoch, portfolio: portfolio, interval:interval};

        $('#save-portfolio').removeClass('unavailable');
        $.ajax({
            type: "POST",
            url: `${_self.url}/backtesting`,
            contentType:"Application/JSON",
            data: kaka,
            success: _self.drawGraph('','container')
            
        });
    });

};
//Appends button functionality
Backtesting.prototype.buttonClick = function(){
    var _self = this;
    $('.buttons').on('mousedown', function(){
        var id = $(this).attr('id');
        $('#'+id).addClass('down');
    });
    $('.buttons').on('mouseup',function(){
        var ade = $(this).attr('id');
        $('#'+ade).removeClass('down');
    });
}


//Using jQuery Datetime picker for date and time selection  
Backtesting.prototype.appendDatetimePicker = function(){
    var _self = this;
    var now = new Date();
        var year = now.getFullYear;
        var month = now.getMonth;
        var day = now.getDate;
        $('#start-date').datetimepicker({
            //format:'Y/m/d H:i',
            onShow:function( ct ){            
                this.setOptions({
                    maxDate: year+"/" +month +"/"+day
                    //maxDate:$('#start-date').val()?$('#end-date').val().substr(0,10):false //,
                    //maxTime:jQuery('#datetime2').val()?jQuery('#datetime2').val():false
                });
            }
        }).attr('readonly','readonly');
        $('#end-date').datetimepicker({
            onShow:function( ct ){
                this.setOptions({
                    minDate:$('#end-date2').val()?$('#start-date2').val().substr(0,10):false,
                    maxDate: year+"/" +month +"/"+day
                    //maxTime: now.getTime
                    //minTime:jQuery('#datetime1').val()?jQuery('#datetime1').val():false
                });
            }
        }).attr('readonly','readonly');
        $('#start-date2').datetimepicker({
            //format:'Y/m/d H:i',
            onShow:function( ct ){            
                this.setOptions({
                    maxDate: year+"/" +month +"/"+day
                    //maxDate:$('#start-date').val()?$('#end-date').val().substr(0,10):false //,
                    //maxTime:jQuery('#datetime2').val()?jQuery('#datetime2').val():false
                });
            }
        }).attr('readonly','readonly');
        $('#end-date2').datetimepicker({
            onShow:function( ct ){
                this.setOptions({
                    minDate:$('#end-date2').val()?$('#start-date2').val().substr(0,10):false,
                    maxDate: year+"/" +month +"/"+day
                    //maxTime: now.getTime
                    //minTime:jQuery('#datetime1').val()?jQuery('#datetime1').val():false
                });
            }
        }).attr('readonly','readonly');
};

//Using Highcharts for profit graph drawal
Backtesting.prototype.drawGraph = function(shortLabels, place) {
    var _self = this;
    return function(dada){
        var detailChart;
        var wholeData = dada;//JSON.parse(dada);
        if (wholeData.message){
            _self.popUpMessage(wholeData.message);
            return;
        }
        _self['portfolioValue'+ shortLabels].roi = wholeData.roi;
        _self['portfolioValue' + shortLabels].profit = wholeData.portfolio;
        _self['portfolioValue' + shortLabels].fees = wholeData.fees;
        _self['portfolioValue' + shortLabels].coins = wholeData.coins;
        var data = wholeData.values;
        var moment = new Date();
        var offset = moment.getTimezoneOffset() ;
        var interval = parseInt(wholeData.interval);
        var portfolioEnd = wholeData.portfolio;
        var roiEnd = wholeData.roi;
        var transactionFees = wholeData.fees;
        $('#portfolio-end'+shortLabels).text('$ ' + portfolioEnd);
        $('#ROI-end'+shortLabels).text(roiEnd + '%');
        $('#fees-end'+shortLabels).text('$ ' + transactionFees);
        for (var i = 0; i<data.length;i++){
            data[i][0] = data[i][0] - (offset-60)*60*1000
        }

        function createDetail(masterChart) {
            
            // prepare the detail chart
            var detailData = [],
                detailStart = data[0][0];

            $.each(masterChart.series[0].data, function () {
                if (this.x >= detailStart) {
                    detailData.push(this.y);
                }
            });

            // create a detail chart referenced by a global variable
            detailChart = Highcharts.chart('detail-container'+shortLabels, {
                chart: {
                    marginBottom: 120,
                    reflow: false,
                    marginLeft: 50,
                    marginRight: 20,
                    style: {
                        position: 'absolute'
                    }
                },
                credits: {
                    enabled: false
                },
                title: {
                    text: 'Total Portfolio in USD'
                },
                subtitle: {
                    text: 'Select an area by dragging across the lower chart'
                },
                xAxis: {
                    type: 'datetime'
                },
                yAxis: {
                    title: {
                        text: null
                    },
                    maxZoom: 0.1
                },
                tooltip: {
                    formatter: function () {
                        var point = this.points[0];
                        return '<b>' + point.series.name + '</b><br/>' + Highcharts.dateFormat('%A %B %e %Y', this.x) + ':<br/>' +
                            'Total Portfolio: ' + Highcharts.numberFormat(point.y, 2) + ' USD';
                    },
                    shared: true
                },
                //turboThreshold: 10000,
                legend: {
                    enabled: false
                },
                plotOptions: {
                    series: {
                        marker: {
                            enabled: false,
                            states: {
                                hover: {
                                    enabled: true,
                                    radius: 3
                                }
                            }
                        }
                    }
                },
                series: [{
                    name: 'Total Portfolio in USD',
                    pointStart: detailStart,
                    pointInterval: 3600 * 1000 * interval,//(data[data.length-1][0]-data[0][0])/100,//24 * 3600 * 1000,
                    data: detailData
                }],

                exporting: {
                    enabled: false
                }

            }); // return chart
        }

        // create the master chart
        function createMaster() {
            Highcharts.chart('master-container'+shortLabels, {
                chart: {
                    reflow: false,
                    borderWidth: 0,
                    backgroundColor: null,
                    marginLeft: 50,
                    marginRight: 20,
                    zoomType: 'x',
                    events: {

                        // listen to the selection event on the master chart to update the
                        // extremes of the detail chart
                        selection: function (event) {
                            var extremesObject = event.xAxis[0],
                                min = extremesObject.min,
                                max = extremesObject.max,
                                detailData = [],
                                xAxis = this.xAxis[0];

                            // reverse engineer the last part of the data
                            $.each(this.series[0].data, function () {
                                if (this.x > min && this.x < max) {
                                    detailData.push([this.x, this.y]);
                                }
                            });

                            // move the plot bands to reflect the new detail span
                            xAxis.removePlotBand('mask-before'+shortLabels);
                            xAxis.addPlotBand({
                                id: 'mask-before'+shortLabels,
                                from: data[0][0],
                                to: min,
                                color: 'rgba(0, 0, 0, 0.2)'
                            });

                            xAxis.removePlotBand('mask-after'+shortLabels);
                            xAxis.addPlotBand({
                                id: 'mask-after'+shortLabels,
                                from: max,
                                to: data[data.length - 1][0],
                                color: 'rgba(0, 0, 0, 0.2)'
                            });


                            detailChart.series[0].setData(detailData);

                            return false;
                        }
                    }
                },
                title: {
                    text: null
                },
                xAxis: {
                    type: 'datetime',
                    showLastTickLabel: true,
                    //maxZoom: 14 * 24 * 3600000, // fourteen days
                    plotBands: [{
                        id: 'mask-before'+shortLabels,
                        from: data[0][0],
                        to: data[data.length - 1][0],
                        color: 'rgba(0, 0, 0, 0.2)'
                    }],
                    title: {
                        text: null
                    }
                },
                yAxis: {
                    gridLineWidth: 0,
                    labels: {
                        enabled: false
                    },
                    title: {
                        text: null
                    },
                    min: 0.6,
                    showFirstLabel: false
                },
                tooltip: {
                    formatter: function () {
                        return false;
                    }
                },
                legend: {
                    enabled: false
                },
                credits: {
                    enabled: false
                },
                plotOptions: {
                    series: {
                        fillColor: {
                            linearGradient: [0, 0, 0, 70],
                            stops: [
                                [0, Highcharts.getOptions().colors[0]],
                                [1, 'rgba(255,255,255,0)']
                            ]
                        },
                        lineWidth: 1,
                        marker: {
                            enabled: false
                        },
                        shadow: false,
                        states: {
                            hover: {
                                lineWidth: 1
                            }
                        },
                        enableMouseTracking: false
                    }
                },

                series: [{
                    type: 'area',
                    name: 'Total Portfolio in USD',
                    pointInterval: 24  * 3600 * 1000,// * interval,
                    pointStart: data[0][0],
                    data: data
                }],

                exporting: {
                    enabled: false
                }

            }, function (masterChart) {
                createDetail(masterChart);
            }); // return chart instance
        }

        // make the container smaller and add a second container for the master chart
        var $container = $('#'+ place)
            .css('position', 'relative');

        $('<div id="detail-container'+shortLabels+'">')
            .appendTo($container);

        $('<div id="master-container'+shortLabels+'">')
            .css({
                position: 'absolute',
                top: 300,
                height: 100,
                width: '100%'
            })
                .appendTo($container);

        // create master and in its callback, create the detail chart
        createMaster();
        }
};

Backtesting.prototype.apply = function(){
    var _self = this;
    
    _self.getCurrencies();
    _self.coinSelection();
    _self.coinRemoval();
    _self.savePortfolio();
    _self.saveAllocations();
    _self.registerFormEffects();
    _self.register();
    _self.login();
    _self.logout();
    _self.byMarketCap();
    _self.equalyWeighted();
    _self.savePortfolio2();
    _self.runBacktesting();
    _self.appendDatetimePicker();
    _self.appendPortfolioDeletion();
    _self.readLocalStorage();
    _self.editPassword();
    _self.changePassword();
    _self.forgotPassword();
    _self.editEmail();
    _self.editFirstname();
    _self.editLastname();
    _self.hidePopUp();
    _self.hideBackground();
    _self.askForVerification();
    _self.buttonClick();
};
$(function(){
    var backtesting = new Backtesting();
    backtesting.apply();
});