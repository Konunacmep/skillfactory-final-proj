exports.dateFormat = function (date) {  // Вывод даты без T и часового пояса
  let formatted = date.split('T')
  return formatted[0] + ' ' + formatted[1].split('+')[0]
}
    
// функция парсинга токена
exports.parseJwt = function (token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
};