export const BASE_URL = "https://493a-122-187-108-202.ngrok-free.app";

export async function request(
	method,
	endpoint,
	data = undefined,
	omitToken = false,
	ContentType = "application/json"
) {
	try {
		const options = {
			method: method,
			headers: {
				"ngrok-skip-browser-warning": "69420",
				"Content-Type": ContentType,
			},
			body: JSON.stringify(data),
		};
		// console.log('options: ', options);

		if (!omitToken)
			options.headers.Authorization = `Bearer ${localStorage.getItem(
				"token"
			)}`;

		const result = await window.fetch(`${BASE_URL}${endpoint}`, options);

		if (result.status >= 200 && result.status < 400) {
			try {
				return [null, await result.json()];
			} catch (err) {
				try {
					return [null, await result.text()];
				} catch (err) {
					return [null, null];
				}
			}
		} else {
			if (result.status === 401) return ["unauthorized", null];
			else return [await result.text(), null];
		}
	} catch (err) {
		console.log(err, err.message);
		return ["network_error", null];
	}
}

// const [err, res] = await request(
// 	'get',
// 	endpoints.GET_CATEGORY(localStorage.getItem('restaurant')),
// )
// console.log(err, res)
// if (err==='network_error'){
// 	// window.alert('check your network and try again')
// 	return
// }
//
// if (err!==null){
// 	// window.alert(JSON.stringify(err)+'\n Contact Us! give this error')
// 	return
// }
// // now you can use res
