$(document).ready(function(){
    var base_header_tour = {
      id: "base-header",
      showPrevButton: true,
      steps: [
        {
          title: "Header",
          content: "This is the header menu of Djanban.",
          target: document.querySelector("#header"),
          placement: "bottom"
        },
        {
          title: "Index",
          content: "Click this icon to go to index",
          target: document.querySelector("#header-menu-index"),
          placement: "bottom"
        },
        {
          title: "Your boards",
          content: "Show a list of your boards. Usually each board is a project wile its lists represent statuses and its tasks move forward (or backwards) through the board.",
          target: document.querySelector("#header-menu-my-boards"),
          placement: "bottom"
        },
        {
          title: "Your multiboards",
          content: "Some projects have several differentiated parts. Create a board for each one of these parts and define a multiboard for the project.",
          target: document.querySelector("#header-menu-multiboards"),
          placement: "bottom"
        },
        {
          title: "Panorama",
          content: "Click here to show a summary of the status of your projects in form of charts.",
          target: document.querySelector("#header-menu-panorama"),
          placement: "bottom"
        },
        {
          title: "Members",
          content: "View a list of the people that works with you.",
          target: document.querySelector("#header-menu-members"),
          placement: "bottom"
        },
        {
          title: "Report recipients",
          content: "Configure what email recipients will receive the daily, weekly and monthly reports.",
          target: document.querySelector("#header-menu-report_recipients"),
          placement: "bottom"
        },
        {
          title: "Development environment",
          content: "Is your office too noisy? Are developers being interrupted by others too much? View that info here.",
          target: document.querySelector("#header-menu-environment"),
          placement: "bottom"
        },
        {
          title: "Niko Niko Calendar",
          content: "Are developers happy/relaxed or are unhappy/stressed? View that info here.",
          target: document.querySelector("#header-menu-niko_niko_calendar"),
          placement: "bottom"
        },
        {
          title: "Slideshow",
          content: "Show this charts as a summary of your current projects.",
          target: document.querySelector("#header-menu-slideshow"),
          placement: "bottom"
        },
        {
          title: "Forecasts",
          content: "Create forecasting models to predict the spent time of your new tasks.",
          target: document.querySelector("#header-menu-forecasts"),
          placement: "bottom"
        },
        {
          title: "Visitors",
          content: "Manage what users can view some board information. Useful to show some information to the clients.",
          target: document.querySelector("#header-menu-visitors"),
          placement: "bottom"
        },
        {
          title: "Hourly rates",
          content: "Define what are the costs per hour for each project.",
          target: document.querySelector("#header-menu-hourly_rates"),
          placement: "bottom"
        },
        {
          title: "Work Hours Packages",
          content: "Manage work packages and be notified when any of them is completed. Very useful for maintenance projects.",
          target: document.querySelector("#header-menu-work_hours_packages"),
          placement: "bottom"
        },
        {
          title: "Fetch",
          content: "Fetch all your boards from Trello. It could take a while.",
          target: document.querySelector("#header-menu-fetch"),
          placement: "bottom"
        },
        {
          title: "Last comments",
          content: "View your last comments in all your boards.",
          target: document.querySelector("#header-menu-last_comments"),
          placement: "bottom"
        },
        {
          title: "Help",
          content: "Show this interactive help.",
          target: document.querySelector("#header-menu-help"),
          placement: "left"
        },
        {
          title: "Log out",
          content: "End your current user session in this site.",
          target: document.querySelector("#header-menu-logout"),
          placement: "left"
        }
      ]
    };

    $("#header #header-menu-help-link").click(function(){
        hopscotch.startTour(base_header_tour);
    });
});