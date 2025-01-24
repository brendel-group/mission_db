export function getHeaders(): {
  "Content-Type": string;
  "X-CSRFToken"?: string;
  Cookie?: string;
} {
  let csrftoken = "";

  // get csrftoken from cookie storage
  try {
    let match_array = document.cookie.match(/csrftoken=[^;]*;/);
    if (match_array && match_array.length > 0) {
      csrftoken = match_array[0]
        .replace("csrftoken=", "")
        .replace(";", "")
        .trim();
    }
  } catch (e) {
    if (!(e instanceof ReferenceError)) {
      // rethrow error if not of expected type
      throw e;
    }
    /*
       ignore ReferenceError because document.cookie may not be defined (when executed on server)
       which will cause a ReferenceError 
       in that case the csrftoken is already passed as argument
      */
  }

  let headers: {
    "Content-Type": string;
    "X-CSRFToken"?: string;
  } = {
    "Content-Type": "application/json",
  };
  if (csrftoken.length > 0) {
    headers["X-CSRFToken"] = csrftoken;
  }
  return headers;
}
