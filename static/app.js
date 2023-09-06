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
		e.preventDefault();
		try {
			const playlistName = $('#name').val();
			const playlistDescription = $('#description').val();

			const dataToSend = {
				playlist_name: playlistName,
				playlist_description: playlistDescription,
				track_id: currentTrackId,
			};
			// if (currentTrackId) {
			// 	dataToSend.track_id = currentTrackId;
			// }
			const response = await axios.post('/playlists/add', dataToSend);
			if (response.status === 200) {
				window.location.reload();
			}
		} catch (error) {
			console.error(error);
		}
	});

	$('.btn-danger').click(async function (event) {
		event.preventDefault();
		const playlistId = $(this).attr('data-playlist-id');
		await deletePlaylist(playlistId);
	});

	async function deletePlaylist(playlistId) {
		try {
			// Use Axios to send the delete request
			const response = await axios.delete(`/playlists/${playlistId}/delete`);

			if (response.status === 200) {
				// Handle successful deletion, e.g., remove the card from the UI
				$(`[data-playlist-id="${playlistId}"]`).closest('.card').remove();
				window.location.reload();
			} else {
				// Handle deletion error, show an error message, etc.
				console.error('Failed to delete playlist.');
			}
		} catch (error) {
			// Handle any errors that may occur during the deletion process
			console.error('An error occurred while deleting the playlist:', error);
		}
	}

	$('.card-img-left').click(async function (e) {
		e.preventDefault();
		let albumId = $(this).closest('.card').find('.card-link').attr('href');
		console.log(albumId);
		window.location.href = albumId;
	});
});

