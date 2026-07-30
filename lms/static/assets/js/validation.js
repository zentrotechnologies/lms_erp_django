function isValidDate(dateString) {
    console.log("sdasd",dateString)
    var regEx = new RegExp(/^\d{2}-\d{2}-\d{4}$/);
    return regEx.test(dateString);
  }

function validateEmail(email) {
  const regularExpression = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return regularExpression.test(String(email).toLowerCase());
  }

  function IsValid(value) {
    if (value == "" || value == null || value == undefined) {
        return true;
    } else {
        return false;
    }
}

function validateGstNumber(gstNumber){
    var gstinformat = new RegExp(/\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}/);   
    return gstinformat.test(gstNumber);
}
   
  $('.numericField').keypress(function (event) {
      var keycode = event.which;
      if (!(event.shiftKey == false && (keycode == 46 || keycode == 8 || keycode == 37 || keycode == 39 || (keycode >= 48 && keycode <= 57)))) {
          event.preventDefault();
      }
  });
  
 
  
  $('.nameField').on('keypress', function (event) {
      var regex = new RegExp("^[a-zA-Z ]+$");
      var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
      if (!regex.test(key)) {
         event.preventDefault();
         return false;
      }
  });

   
  $('.billField').on('keypress', function (event) {
    var regex = new RegExp("^[a-zA-Z0-9-/]+$");
    var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
    if (!regex.test(key)) {
       event.preventDefault();
       return false;
    }
});

   
$('.emailField').on('keypress', function (event) {
    var regex = new RegExp("^[a-zA-Z0-9@.]+$");
    var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
    if (!regex.test(key)) {
       event.preventDefault();
       return false;
    }
});
  
  
  $('.textField').on('keypress', function (event) {
      var regex = new RegExp("^[a-zA-Z ]+$");
      var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
      if (!regex.test(key)) {
         event.preventDefault();
         return false;
      }
  });
  
  
  
  $('.codeField').on('keypress', function (event) {
      var regex = new RegExp("^[a-zA-Z0-9 ]+$");
      var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
      if (!regex.test(key)) {
         event.preventDefault();
         return false;
      }
  });

  function numericField(event){
    var keycode = event.which;
    if (!(event.shiftKey == false && (keycode == 46 || keycode == 8 || keycode == 37 || keycode == 39 || (keycode >= 48 && keycode <= 57)))) {
        event.preventDefault();
    }
  }



$("div.kt_datatable_filter input").focus();


// const baseEncryptionKey = CryptoJS.enc.Base64.parse('{{base_encryption_key}}');

// const base_iv = CryptoJS.enc.Hex.parse('00000000000000000000000000000000');

// function encryptData(data) {
//     const encrypted = CryptoJS.AES.encrypt(data, baseEncryptionKey, {
//         iv: base_iv,
//         mode: CryptoJS.mode.CBC,
//         padding: CryptoJS.pad.Pkcs7,
//     });
//     return encrypted.toString();
// }

// function decryptData(encryptedData) {
//     const decrypted = CryptoJS.AES.decrypt(encryptedData, baseEncryptionKey, {
//         iv: base_iv,
//         mode: CryptoJS.mode.CBC,
//         padding: CryptoJS.pad.Pkcs7,
//     });
//     return decrypted.toString(CryptoJS.enc.Utf8);
// }



// const baseEncryptionKey = 'D3KyP1sPstZZa4Yf2u0E0unfXgR9L5SS'


// function encryptData(data) {
//     debugger;
//     console.log("dassssa",data,baseEncryptionKey)
//     if (typeof data !== 'string') {
//         data = JSON.stringify(data); // Ensure data is a string
//     }
    
//     const encrypted = CryptoJS.AES.encrypt(data, baseEncryptionKey).toString();
//     return encrypted;
// }

// function decryptData(encryptedData) {
//     const bytes = CryptoJS.AES.decrypt(encryptedData, baseEncryptionKey);
//     const decrypted = bytes.toString(CryptoJS.enc.Utf8);
//     return decrypted;
// }

// const baseEncryptionKey = 'D3KyP1sPstZZa4Yf2u0E0unfXgR9L5SS'
const baseEncryptionKey = 'D3KyP1sPstZZa4Yf2u0E0unfXgR9L5s2iIpoU-W5_Yc='
const baseEncryptionIv = 'PstZa4Yf2uE0unfX'

const base_fernet_secret_key = new fernet.Secret(baseEncryptionKey);

function encryptData(message) {
    try {
        // Create the secret using the provided key
        //const secret = new fernet.Secret(secretKey);

        // Create a Fernet token object with a fixed IV and time (if needed)
        const token = new fernet.Token({
            secret: base_fernet_secret_key,
            time: Date.now(), // Use the current time
            iv: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], // Example fixed IV
        });

        // Encode and return the encrypted token
        return token.encode(message);
    } catch (error) {
        console.error("Error encoding Fernet message:", error.message);
        return null; // Return null in case of an error
    }
}

function decryptData(encryptedToken) {
 
    try {
        // Create the secret using the provided key
        //const secret = new fernet.Secret(secretKey);

        // Create a Fernet token object
        const token = new fernet.Token({
            secret: base_fernet_secret_key,
            token: encryptedToken,
            ttl: 0 // Set TTL to 0 for no expiration time
        });

        // Decode and return the decrypted message
        return token.decode();
    } catch (error) {
        console.error("Error decoding Fernet token:", error.message);
        return null; // Return null in case of an error
    }
}