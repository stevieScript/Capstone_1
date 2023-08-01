$(document).ready(function () {
	const myModalElement = $('#myModal');
	const playlistForm = $('#playlist-form');
	const search = $('#search');
	const createPlaylistForm = $('#create-add-playlist');

	let currentTrackId = null;

	$('[id^="like-icon-"]').on('click', async function (e) {
		e.preventDefault();

		const song_id = $(this).data('track-id');
		const icon = $(this);
		if (!song_id) {
			console.error('No song ID found');
			return;
		}

		let response;
		if ($(this).hasClass('far')) {
			response = await axios.post(`/songs/${song_id}/like`);
			if (response.status === 200) {
				icon.removeClass('far').addClass('fas');
			}
		} else {
			response = await axios.post(`/songs/${song_id}/unlike`);
			if (response.status === 200) {
				icon.removeClass('fas').addClass('far');
			}
		}
	});

	myModalElement.on('shown.bs.modal', function (e) {
		const button = $(e.relatedTarget);
		currentTrackId = button.data('track-id');
	});

	playlistForm.on('submit', async function (e) {
		e.preventDefault();
		const playlist_id = $('#playlist').val();

		if (!currentTrackId) {
			console.error('No track ID found');
			return;
		}

		const res = await axios.post(`/songs/${currentTrackId}`, {
			track_id: currentTrackId,
			playlist_id: playlist_id,
		});
	});

	search.on('submit', function (e) {
		e.preventDefault();
	});

	createPlaylistForm.on('submit', async function (e) {
		// e.preventDefault();
		const playlistName = $('#name').val();
		const playlistDescription = $('#description').val();

		const dataToSend = {
			playlist_name: playlistName,
			playlist_description: playlistDescription,
		};
		if (currentTrackId) {
			dataToSend.track_id = currentTrackId;
		}
		const response = await axios.post('/playlists/add', dataToSend);
	});
});

