$(document).ready(function () {
	console.log('DOM loaded');
	const myModalElement = $('#myModal');
	const playlistForm = $('#playlist-form');
	const search = $('#search');
	const createPlaylistForm = $('#create-add-playlist');

	let currentTrackId = null;

	myModalElement.on('shown.bs.modal', function (e) {
		const button = $(e.relatedTarget);
		currentTrackId = button.data('track-id');
		console.log(currentTrackId);
	});

	playlistForm.on('submit', async function (e) {
		e.preventDefault();
		console.log('Adding track to playlist');
		const playlist_id = $('#playlist').val();

		if (!currentTrackId) {
			console.error('No track ID found');
			return;
		}

		const res = await axios.post(`/audio_analysis/${currentTrackId}`, {
			track_id: currentTrackId,
			playlist_id: playlist_id,
		});
		console.log(res.data);
	});

	search.on('submit', function (e) {
		e.preventDefault();
	});

	createPlaylistForm.on('submit', async function (e) {
		e.preventDefault();
		console.log('Creating playlist');
		const playlistName = $('#name').val();
		const playlistDescription = $('#description').val();

		const dataToSend = {
			playlist_name: playlistName,
			playlist_description: playlistDescription,
			track_id: currentTrackId,
		};

		console.log('Sending data:', dataToSend);

		const response = await axios.post('/user/playlists/add', dataToSend);
		// debugger;
		console.log(response.data);
	});
});
