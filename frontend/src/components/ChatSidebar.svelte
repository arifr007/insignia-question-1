<script>
  import { chatRooms, currentRoom, sidebarVisible, chatRoomStore } from '../stores/index.js';

  let editingRoomId = null;
  let editingTitle = '';

  async function selectRoom(room) {
    try {
      await chatRoomStore.selectRoom(room.id);
    } catch (error) {
      console.error('Failed to select room:', error);
    }
  }

  async function deleteRoom(room, event) {
    event.stopPropagation();

    if (confirm(`Delete chat "${room.title}"?`)) {
      try {
        await chatRoomStore.deleteRoom(room.id);
      } catch (error) {
        console.error('Failed to delete room:', error);
      }
    }
  }

  function startEditingTitle(room, event) {
    event.stopPropagation();
    editingRoomId = room.id;
    editingTitle = room.title;
  }

  async function saveTitle(room) {
    if (editingTitle.trim() && editingTitle !== room.title) {
      try {
        await chatRoomStore.updateRoomTitle(room.id, editingTitle.trim());
      } catch (error) {
        console.error('Failed to update title:', error);
      }
    }
    editingRoomId = null;
    editingTitle = '';
  }

  function handleTitleKeyPress(event, room) {
    if (event.key === 'Enter') {
      saveTitle(room);
    } else if (event.key === 'Escape') {
      editingRoomId = null;
      editingTitle = '';
    }
  }

  function formatRelativeTime(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  }

  async function createNewRoom() {
    try {
      const room = await chatRoomStore.createRoom();
      if (room) {
        await chatRoomStore.selectRoom(room.id);
      }
    } catch (error) {
      console.error('Failed to create room:', error);
    }
  }
</script>

{#if $sidebarVisible}
  <!-- Overlay for mobile -->
  <button
    type="button"
    class="fixed inset-0 bg-black/50 z-[999] md:hidden"
    on:click={chatRoomStore.toggleSidebar}
    aria-label="Close sidebar"
    tabindex="0"
    style="all: unset; display: block;"
  ></button>
{/if}

<div
  class="fixed top-0 left-0 w-[280px] sm:w-[300px] md:w-[320px] lg:w-[360px] xl:w-[400px] h-screen bg-slate-900/95 backdrop-blur-sm border-r border-white/20 transition-transform duration-300 z-[1000] flex flex-col {$sidebarVisible
    ? 'translate-x-0'
    : '-translate-x-full'}"
>
  <div class="p-3 border-b border-white/20 flex justify-between items-center flex-shrink-0">
    <h2 class="m-0 text-lg text-white font-semibold">💬 Chat History</h2>
    <button
      class="bg-transparent border-none text-white/70 text-xl cursor-pointer p-2 rounded transition-all hover:bg-white/10 hover:text-white flex items-center justify-center w-10 h-10"
      on:click={chatRoomStore.toggleSidebar}
      title="Close sidebar">✕</button
    >
  </div>

  <div class="p-3 border-b border-white/10 flex-shrink-0">
    <button
      class="w-full p-3 bg-blue-600 text-white border-none rounded-lg font-medium cursor-pointer transition-all hover:bg-blue-700 hover:-translate-y-0.5 text-sm"
      on:click={createNewRoom}
    >
      + New Chat
    </button>
  </div>

  <div
    class="flex-1 overflow-y-auto py-2 [scrollbar-width:thin] [scrollbar-color:rgb(255_255_255_/_0.2)_transparent] [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-white/20 [&::-webkit-scrollbar-thumb]:rounded [&::-webkit-scrollbar-thumb:hover]:bg-white/30"
  >
    {#if $chatRooms.length === 0}
      <div class="py-10 px-4 text-center text-white/60">
        <p class="my-2 text-sm">No chat history yet</p>
        <p class="my-2 text-sm">Start a conversation!</p>
      </div>
    {:else}
      {#each $chatRooms as room (room.id)}
        <div
          class="group flex items-start w-full text-left p-3 mx-2 my-1 rounded-lg cursor-pointer transition-all bg-transparent border border-transparent hover:bg-white/5 hover:border-white/10 {$currentRoom?.id ===
          room.id
            ? 'bg-blue-600/20 border-blue-600/30'
            : ''}"
        >
          <button
            type="button"
            class="flex-1 min-w-0 overflow-hidden text-left bg-transparent border-none cursor-pointer p-0"
            on:click={() => selectRoom(room)}
            on:keydown={e => {
              if (e.key === 'Enter' || e.key === ' ') {
                selectRoom(room);
              }
            }}
            aria-label={`Select chat room: ${room.title}`}
          >
            <div class="flex-1 min-w-0 overflow-hidden">
              {#if editingRoomId === room.id}
                <textarea
                  class="w-full bg-white/10 border border-white/30 rounded p-2 text-white text-sm font-medium focus:outline-none focus:border-blue-600 focus:bg-white/15 resize-none min-h-[2.5rem] max-h-[6rem] leading-tight break-words [hyphens:auto]"
                  bind:value={editingTitle}
                  on:keydown={e => handleTitleKeyPress(e, room)}
                  on:blur={() => saveTitle(room)}
                  placeholder="Enter chat title..."
                ></textarea>
              {:else}
                <div
                  class="text-white font-medium mb-2 leading-tight text-left overflow-hidden break-words [hyphens:auto] text-sm line-clamp-3"
                  title={room.title}
                >
                  {room.title}
                </div>
              {/if}

              <div class="flex gap-2 items-center text-xs text-white/60 flex-wrap">
                <span class="font-medium text-left">{formatRelativeTime(room.updated_at)}</span>
                {#if room.message_count > 0}
                  <span class="bg-white/10 px-1.5 py-0.5 rounded-full text-[10px] whitespace-nowrap"
                    >{room.message_count} messages</span
                  >
                {/if}
              </div>
            </div>
          </button>

          <div
            class="flex flex-col gap-1 opacity-0 transition-opacity group-hover:opacity-100 flex-shrink-0 ml-2"
          >
            <button
              class="bg-transparent border-none p-1.5 rounded cursor-pointer text-sm transition-all text-white/60 hover:bg-white/10 hover:text-white flex items-center justify-center w-8 h-8"
              on:click={e => startEditingTitle(room, e)}
              title="Edit title"
              type="button"
            >
              ✏️
            </button>
            <button
              class="bg-transparent border-none p-1.5 rounded cursor-pointer text-sm transition-all text-white/60 hover:bg-red-500/20 hover:text-red-300 flex items-center justify-center w-8 h-8"
              on:click={e => deleteRoom(room, e)}
              title="Delete chat"
              type="button"
            >
              🗑️
            </button>
          </div>
        </div>
      {/each}
    {/if}
  </div>
</div>
