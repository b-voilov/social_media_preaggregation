
--
-- Name: youtube_channels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.youtube_channels (
    id character varying(255) NOT NULL,
    title character varying(255),
    description_channel text,
    custom_url character varying(255),
    published_at timestamp without time zone,
    default_language character varying(255),
    country character varying(255),
    view_count bigint,
    subscriber_count integer,
    video_count integer
);



--
-- Name: youtube_comments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.youtube_comments (
    id character varying(255) NOT NULL,
    text_display text,
    like_count integer,
    published_at timestamp without time zone,
    updated_at timestamp without time zone,
    parent_id character varying(255),
    video_id character varying(255),
    pos_sentiment double precision,
    neg_sentiment double precision
);



--
-- Name: youtube_videos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.youtube_videos (
    id character varying(255) NOT NULL,
    published_at timestamp without time zone,
    channel_id character varying(255),
    channel_title character varying(255),
    title character varying(255),
    description_video text,
    duration character varying(255),
    definition_video character varying(255),
    default_audio_language character varying(255),
    view_count bigint,
    like_count integer,
    dislike_count integer,
    favorite_count integer,
    comment_count integer,
    recording_date timestamp without time zone,
    speech_text text,
    title_pos_sentiment double precision,
    title_neg_sentiment double precision,
    description_pos_sentiment integer,
    description_neg_sentiment integer,
    speech_pos_sentiment double precision,
    speech_neg_sentiment double precision
);

--
-- Name: youtube_channels youtube_channels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.youtube_channels
    ADD CONSTRAINT youtube_channels_pkey PRIMARY KEY (id);


--
-- Name: youtube_comments youtube_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.youtube_comments
    ADD CONSTRAINT youtube_comments_pkey PRIMARY KEY (id);


--
-- Name: youtube_videos youtube_videos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.youtube_videos
    ADD CONSTRAINT youtube_videos_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

